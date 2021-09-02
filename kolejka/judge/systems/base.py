# vim:ts=4:sts=4:sw=4:expandtab


from copy import deepcopy
import datetime
import grp
import io
import json
import logging
import os
import pathlib
import pwd
import shutil
import sys
import tempfile
import threading
import time


from kolejka.judge import config
from kolejka.judge.exceptions import *
from kolejka.judge.paths import *
from kolejka.judge.result import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'SystemBase' ]
def __dir__():
    return __all__


class SystemBase(AbstractSystem):
    def __init__(self, output_directory=None, environment=None, paths=None):
        self._output_directory = pathlib.Path(output_directory or '.').resolve()
        self._environment = dict(environment or {})
        self._users = set()
        self._users_homes = dict()
        self._groups = set()
        self._paths = set(paths or [])
        self.validators = self.Validators(self)
        self._background = dict()

    @property
    def output_directory(self):
        return self.get_output_directory()
    def get_output_directory(self):
        return self._output_directory

    @property
    def program_path(self):
        return self.get_program_path()
    def get_program_path(self):
        return ':'.join([ path for path in [
            str(self.resolve_path(get_output_path(config.SHARED)) / 'sbin'),
            str(self.resolve_path(get_output_path(config.SHARED)) / 'bin'),
            '/usr/local/sbin','/usr/local/bin','/usr/local/cuda/bin','/usr/sbin','/usr/bin','/sbin','/bin'
        ] if os.path.isdir(path) ])

    @property
    def program_library_path(self):
        return self.get_program_library_path()
    def get_program_library_path(self):
        return ':'.join([ path for path in [
            str(self.resolve_path(get_output_path(config.SHARED)) / 'lib'),
        ] if os.path.isdir(path) ])

    @property
    def program_include_path(self):
        return self.get_program_include_path()
    def get_program_include_path(self):
        return ':'.join([ path for path in [
            str(self.resolve_path(get_output_path(config.SHARED)) / 'include'),
        ] if os.path.isdir(path) ])

    @property
    def environment(self):
        return self.get_environment()
    def get_environment(self):
        environment = deepcopy(self._environment)
        environment['PATH'] = self.program_path
        environment['LD_LIBRARY_PATH'] = self.program_library_path
        environment['LIBRARY_PATH'] = self.program_library_path
        environment['CPATH'] = self.program_include_path
        environment['LANG'] = 'en_US.UTF-8'
        return environment

    @property
    def superuser(self):
        return self.get_superuser()
    def get_superuser(self):
        raise NotImplementedError

    @property
    def current_user(self):
        return self.get_current_user()
    def get_current_user(self):
        raise NotImplementedError

    @property
    def users(self):
        return self.get_users()
    def get_users(self):
        return self._users
    def add_user(self, user, home):
        self._users.add(user)
        self._users_homes[user] = home

    @property
    def groups(self):
        return self.get_groups()
    def get_groups(self):
        return self._groups
    def add_group(self, group):
        self._groups.add(group)

    @property
    def paths(self):
        return self.get_paths()
    def get_paths(self):
        return self._paths
    def add_path(self, path):
        self._paths.add(str(get_input_path(path).path))

    @property
    def log_directory(self):
        return self.get_log_directory()
    def get_log_directory(self):
        return get_output_path(config.LOG)

    def resolve_path(self, path, work_directory =None):
        if not work_directory:
            work_directory = get_output_path('.')
        if not path:
            return pathlib.Path('/dev/null')
        if isinstance(path, InputPath):
            return pathlib.Path(path.path)
        if isinstance(path, OutputPath):
            return self.output_directory / path.path
        if isinstance(path, RelativePath):
            return self.output_directory / work_directory.path / path.path
        return pathlib.Path(path)

    def find_files(self, path, work_directory =None):
        rpath = self.resolve_path(path, work_directory=work_directory)
        if not rpath.exists():
            return
        stack = [ rpath ]
        dev = rpath.stat().st_dev
        while stack:
            cpath = stack.pop()
            if cpath.is_symlink():
                continue
            elif cpath.stat().st_dev != dev:
                continue
            elif cpath.is_dir():
                stack += cpath.iterdir()
            elif cpath.is_file():
                yield path / (cpath.relative_to(rpath))

    def file_contents(self, path, work_directory =None):
        rpath = self.resolve_path(path, work_directory=work_directory)
        if not rpath.is_file():
            return None
        return rpath.read_bytes()

    def resolve(self, obj, work_directory =None):
        if isinstance(obj, AbstractPath):
            return str(self.resolve_path(obj, work_directory=work_directory))
        if isinstance(obj, str):
            return obj
        return ''.join([ self.resolve(part, work_directory=work_directory) for part in obj ])
    
    def update_limits(self, limits =None):
        return limits

    def run_step(self, name, step):
        if isinstance(step, AbstractCommand):
            return self.run_command(step, name=name)
        if isinstance(step, AbstractTask):
            result = self.run_task(step, name=name)
            if (result is not None) and (result.status is not None):
                return result
            if step.record_result:
                return result
            else:
                return None
        raise RuntimeError('Step is neither Command nor Task')

    def run_steps(self, steps):
        result = ResultDict()
        for name, step in steps.items():
            if result.status is None or step.obligatory:
                step_result = self.run_step(name, step)
                result.set(name, step_result)
                if result.status is None and step_result and step_result.status is not None:
                    result.set_status(step_result.status)
        if result.status is None:
            result.set_status('OK')
        return result

    def terminate_background(self, background):
        if background in self._background:
            thread, process = self._background[background]
            self.terminate_command(process)

    def wait_background(self, background):
        if background in self._background:
            thread, process = self._background[background]
            del self._background[background]
            thread.join()

    def clear_background(self):
        backgrounds = list(self._background.keys())
        for background in backgrounds:
            self.terminate_background(background)
        for background in backgrounds:
            self.wait_background(background)

    def run_command(self, command, name):
        self.validators.set_work_directory(command.work_directory)
        command.set_name(name)
        command.set_system(self)
        command.sequence_id

        exit_status = None
        result = None

        command.verify_prerequirements()
        command_line = command.resolved_command
        if command_line:
            command_file = self.write_file(command.get_log_path('cmd'), text=True)
            try:
                command_file.write('Command:\n')
                command_file.write(repr(command)+'\n')
                command_file.write('\n\nCommand line:\n')
                command_file.write(repr(command.command))
                if command.stdin:
                    command_file.write(' < '+repr(command.stdin))
                if command.stdout:
                    command_file.write(' >'+('>' if command.stdout_append else ''))
                    command_file.write(' '+repr(command.stdout))
                    if command.stdout_max_bytes is not None:
                        command_file.write(' ['+str(command.stdout_max_bytes)+']')
                if command.stderr:
                    command_file.write(' 2>'+('>' if command.stderr_append else ''))
                    command_file.write(' '+repr(command.stderr))
                    if command.stderr_max_bytes is not None:
                        command_file.write(' ['+str(command.stderr_max_bytes)+']')
                command_file.write('\n')
                debug_line = repr(command_line)
                if command.stdin:
                    debug_line += ' < '+str(command.stdin_path)
                if command.stdout:
                    debug_line += ' > '+str(command.stdout_path)
                if command.stderr:
                    debug_line += ' 2> '+str(command.stderr_path)
                logging.info(debug_line)
                command_file.write('\n\nResolved command line:\n')
                command_file.write(debug_line+'\n')
                command_file.write('\n\nPrerequirements:\n')
                for prerequirement in command.prerequirements:
                    command_file.write(str(prerequirement)+'\n')
                command_file.write('\n\nPostconditions:\n')
                for postcondition in command.postconditions:
                    command_file.write(str(postcondition)+'\n')
                limits = self.update_limits(command.limits)
                environment = command.update_environment(self.environment)
                result = Result(
                        args = command_line,
                        work_directory = command.work_path,
                        environment = environment,
                        user = command.user,
                        group = command.group,
                        limits = limits,
                        stdin = command.stdin_path,
                        stdout = command.stdout_path,
                        stderr = command.stderr_path,
                    )
                command_file.flush()
                if command.safe and not command.background:
                    self.execute_safe_command(
                        command_line,
                        command.stdin_path,
                        command.stdout_path,
                        command.stdout_append,
                        command.stdout_max_bytes,
                        command.stderr_path,
                        command.stderr_append,
                        command.stderr_max_bytes,
                        environment,
                        command.work_path,
                        command.user,
                        command.group,
                        limits,
                        result,
                    )
                else:
                    process = self.start_command(
                        command_line,
                        command.stdin_path,
                        command.stdout_path,
                        command.stdout_append,
                        command.stdout_max_bytes,
                        command.stderr_path,
                        command.stderr_append,
                        command.stderr_max_bytes,
                        environment,
                        command.work_path,
                        command.user,
                        command.group,
                        limits,
                    )
                    if command.background:
                        def finalize():
                            self.wait_command(process, result)
                            command_file.write('\n\nResult:\n')
                            command_file.write(repr(result)+'\n')
                            command_file.close()
                        thread = threading.Thread(target=finalize)
                        thread.start()
                        self._background[command.name] = thread, process
                        return result
                    self.wait_command(process, result)
                command_file.write('\n\nResult:\n')
                command_file.write(repr(result)+'\n')
            finally:
                if not command.background:
                    command_file.close()

            command.set_result(result)
            exit_status = command.verify_postconditions()
            result.set_status(exit_status)

        self.validators.set_work_directory(None)
        return result

    def execute_safe_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result):
        return self.execute_command(command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result)

    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result):
        process = self.start_command(command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits)
        return self.wait_command(process, result)

    def start_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits):
        raise NotImplementedError

    def terminate_command(self, process):
        raise NotImplementedError

    def wait_command(self, process, result):
        raise NotImplementedError

    def run_task(self, task, name):
        task.set_name(name)
        task.set_system(self)
        task.verify_prerequirements()
        result = task.execute()
        return result

    def read_file(self, path, work_directory =None, text =False):
        if not isinstance(path, pathlib.Path):
            path = self.resolve_path(path, work_directory)
        mode = 'rb'
        if text:
            mode = 'r'
        return path.open(mode)
    def write_file(self, path, append =False, work_directory =None, text =False):
        if not isinstance(path, pathlib.Path):
            path = self.resolve_path(path, work_directory)
        path.parent.mkdir(exist_ok=True, parents=True)
        mode = 'wb'
        if text:
            mode = 'w'
        if append:
            mode += 'a'
        return path.open(mode)
    def file_writer(self, path, append =False, work_directory =None, max_bytes =None):
        if not isinstance(path, pathlib.Path):
            path = self.resolve_path(path, work_directory)
        path.parent.mkdir(exist_ok=True, parents=True)
        mode = 'wb'
        if append:
            mode += 'a'
        fd_read, fd_write = os.pipe()
        def writer():
            bytes = 0
            with path.open(mode) as output:
                while True:
                    data = os.read(fd_read, 65536)
                    if not data:
                        break
                    if max_bytes is not None:
                        if bytes < max_bytes:
                            data = data[0:max_bytes-bytes]
                        else:
                            data = b''
                    bytes += len(data)
                    output.write(data)
            os.close(fd_read)
        w = threading.Thread(target=writer)
        w.start()
        return (io.FileIO(fd_write, mode='wb', closefd=True), w)

    def get_user_group_groups(self, user=None, group=None):
        if not self.superuser:
            return None, None, None
        if os.getuid() != 0:
            return None, None, None
        uid = None
        gid = None
        groups = None
        if user:
            try:
                pw = pwd.getpwuid(int(user))
            except:
                pw = pwd.getpwnam(str(user))
            uid = pw.pw_uid
            user = pw.pw_name
            gid = pw.pw_gid
        if group:
            try:
                gr = grp.getgrgid(int(group))
            except:
                gr = grp.getgrnam(group)
            gid = gr.gr_gid
        groups = [ gid ] if gid is not None else None
        if user is not None:
            try:
                groups = os.getgrouplist(user, gid)
            except:
                pass
        return (uid, gid, groups)

    def get_home(self, user=None):
        if user is None:
            return None
        home = self._users_homes.get(user, None)
        if home is None:
            try:
                home = pwd.getpwnam(user).pw_home
            except:
                pass
        return home

    class Validators:
        def __init__(self, system, path=None):
            self._system = system
            self._work_directory = get_output_path(path or '.')

        @property
        def system(self):
            return self.get_system()
        def get_system(self):
            return self._system

        @property
        def work_directory(self):
            return self.get_work_directory()
        def get_work_directory(self):
            return self._work_directory
        def set_work_directory(self, path):
            self._work_directory = get_output_path(path or '.')

        def resolve_path(self, path):
            return self.system.resolve_path(path, work_directory=self.work_directory)

        def noop_validator(self, *args, **kwargs):
            return True

        def file_exists(self, path):
            if isinstance(path, InputPath):
                return self.system_path_exists(path)
            path = self.resolve_path(path)
            return path.is_file() or path == pathlib.Path('/dev/null')

        def directory_exists(self, path):
            return self.resolve_path(path).is_dir()

        def program_exists(self, path):
            path = self.resolve_path(path)
            return path.is_file() and ( path.stat().st_mode & 0o111 )

        def file_empty(self, path):
            path = self.resolve_path(path)
            return not path.is_file() or path.stat().st_size < 1

        def file_does_not_match(self, path, regexes):
            path = self.resolve_path(path)
            if not path.is_file():
                return True
            try:
                with path.open() as path_file:
                    for line in path_file:
                        for regex in regexes:
                            if regex.fullmatch(line):
                                return False
            except:
                pass
            return True

        def system_group_exists(self, group):
            return group in self.system.groups

        def system_user_exists(self, user):
            return user in self.system.users

        def system_path_exists(self, path):
            path = str(get_input_path(path).path)
            return path in self.system.paths or path=='/dev/null'

        def system_program_exists(self, path):
            return shutil.which(path, path=self.system.program_path) is not None

        def __getattr__(self, item):
            return self.noop_validator

# vim:ts=4:sts=4:sw=4:expandtab
from contextlib import ExitStack
from copy import deepcopy
import datetime
import grp
import json
import logging
import os
import pathlib
import pwd
import shutil
import subprocess
import sys
import tempfile
import threading
import time
assert sys.version_info >= (3, 6)


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

    @property
    def output_directory(self) -> pathlib.Path:
        return self.get_output_directory()
    def get_output_directory(self):
        return self._output_directory

    @property
    def program_path(self) -> str:
        return self.get_program_path()
    def get_program_path(self):
        return '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

    @property
    def environment(self) -> Dict[str, Optional[Resolvable]]:
        return self.get_environment()
    def get_environment(self):
        environment = deepcopy(self._environment)
        environment['PATH'] = self.program_path
        environment['LANG'] = 'en_US.UTF-8'
        return environment

    @property
    def superuser(self) -> bool:
        return self.get_superuser()
    def get_superuser(self):
        raise NotImplementedError

    @property
    def users(self) -> Set[str]:
        return self.get_users()
    def get_users(self):
        return self._users
    def add_user(self, user: str, home: str):
        self._users.add(user)
        self._users_homes[user] = home

    @property
    def groups(self) -> Set[str]:
        return self.get_groups()
    def get_groups(self):
        return self._groups
    def add_group(self, group: str):
        self._groups.add(group)

    @property
    def paths(self) -> Set[str]:
        return self.get_paths()
    def get_paths(self):
        return self._paths
    def add_path(self, path):
        self._paths.add(str(get_input_path(path).path))

    @property
    def log_directory(self) -> OutputPath:
        return self.get_log_directory()
    def get_log_directory(self):
        return get_output_path('log')

    def resolve_path(self, path: Optional[AbstractPath], work_directory: Optional[OutputPath] =None) -> pathlib.Path:
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

    def find_files(self, path: AbstractPath, work_directory: Optional[OutputPath] =None) -> Generator[AbstractPath, None, None]:
        rpath = self.resolve_path(path, work_directory=work_directory)
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

    def resolve(self, obj: Resolvable, work_directory: Optional[OutputPath] =None) -> str:
        if isinstance(obj, AbstractPath):
            return str(self.resolve_path(obj, work_directory=work_directory))
        if isinstance(obj, str):
            return obj
        return ''.join([ self.resolve(part, work_directory=work_directory) for part in obj ])
    
    def update_limits(self, limits: Optional[AbstractLimits] =None) -> AbstractLimits:
        return limits

    def run_step(self, step, name):
        if isinstance(step, AbstractCommand):
            return self.run_command(step, name=name)
        if isinstance(step, AbstractTask):
            return self.run_task(step, name=name)
        raise RuntimeError('Step is neither Command nor Task')

    def run_steps(self, steps):
        result = {}
        for name, step in steps.items():
            exit_status, result[name] = self.run_step(step, name)
            if exit_status is not None:
                return exit_status, result

        return 'OK', result

    def run_command(self, command: AbstractCommand, name: str):
        self.validators.set_work_directory(command.work_directory)
        command.set_name(name)
        command.set_system(self)
        command.sequence_id

        exit_status = None
        result = None

        command.verify_prerequirements()
        command_line = command.resolved_command
        if command_line:
            with self.write_file(command.get_log_path('cmd')) as command_file:
                command_file.write('Command:\n')
                command_file.write(repr(command)+'\n')
                command_file.write('\n\nCommand line:\n')
                command_file.write(repr(command.command))
                if command.stdin:
                    command_file.write(' < '+repr(command.stdin))
                if command.stdout:
                    command_file.write(' > '+repr(command.stdout))
                if command.stderr:
                    command_file.write(' 2> '+repr(command.stderr))
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
                self.execute_command(
                    command_line,
                    command.stdin_path,
                    command.stdout_path,
                    command.stdout_append,
                    command.stderr_path,
                    command.stderr_append,
                    environment,
                    command.work_path,
                    command.user,
                    command.group,
                    limits,
                    result,
                )
                command.set_result(result)
                command_file.write('\n\nResult:\n')
                command_file.write(repr(result)+'\n')

            exit_status = command.verify_postconditions()

        self.validators.set_work_directory(None)
        return exit_status, result

    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits):
        raise NotImplementedError

    def run_task(self, task: AbstractTask, name: str):
        task.set_name(name)
        task.set_system(self)
        task.verify_prerequirements()
        return task.execute()

    def read_file(self, path: Optional[Union[pathlib.Path,AbstractPath]], work_directory: Optional[OutputPath] =None):
        if not isinstance(path, pathlib.Path):
            path = self.resolve_path(path, work_directory)
        return path.open('r')
    def write_file(self, path: Optional[Union[pathlib.Path,AbstractPath]], append: Optional[bool] =False, work_directory: Optional[OutputPath] =None):
        if not isinstance(path, pathlib.Path):
            path = self.resolve_path(path, work_directory)
        path.parent.mkdir(exist_ok=True, parents=True)
        mode = 'w'
        if append:
            mode += 'a'
        return path.open(mode)

    def get_uid_gid_groups(self, user=None, group=None):
        if not self.superuser:
            return None, None, None
        uid = None
        gid = None
        groups = None
        try:
            uid = pwd.getpwnam(user).pw_uid if user is not None else None
        except:
            pass
        try:
            gid = grp.getgrnam(group).gr_gid if group is not None else None
        except:
            pass
        try:
            groups = [ gid ] if group is not None else None
        except:
            pass
        if user:
            try:
                groups = os.getgrouplist(user, gid) if gid is not None else os.getgrouplist(user)
            except:
                pass
        return (uid, gid, groups)

    @staticmethod
    def get_change_user_function(user=None, group=None):
        if os.getuid() != 0:
            return None
        if user is None and group is None:
            return None

        uid, gid, groups = self.get_uid_gid_groups(user=user, group=group)
        def change_user():
            try:
                if groups is not None:
                    os.setgroups(groups)
                if gid is not None:
                    os.setgid(gid)
                if uid is not None:
                    os.setuid(uid)
                os.setsid()
            except OSError:
                pass
        return change_user

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
        def system(self) -> AbstractSystem:
            return self.get_system()
        def get_system(self):
            return self._system

        @property
        def work_directory(self) -> OutputPath:
            return self.get_work_directory()
        def get_work_directory(self):
            return self._work_directory
        def set_work_directory(self, path):
            self._work_directory = get_output_path(path or '.')

        def resolve_path(self, path: Optional[AbstractPath]) -> pathlib.Path:
            return self.system.resolve_path(path, work_directory=self.work_directory)

        def noop_validator(self, *args, **kwargs) -> bool:
            return True

        def file_exists(self, path) -> bool:
            if isinstance(path, InputPath):
                return self.system_path_exists(path)
            path = self.resolve_path(path)
            return path.is_file() or path == pathlib.Path('/dev/null')

        def directory_exists(self, path) -> bool:
            return self.resolve_path(path).is_dir()

        def program_exists(self, path) -> bool:
            path = self.resolve_path(path)
            return path.is_file() and ( path.stat().st_mode & 0o111 )

        def file_empty(self, path) -> bool:
            path = self.resolve_path(path)
            return not path.is_file() or path.stat().st_size < 1

        def file_does_not_match(self, path, regexes) -> bool:
            path = self.resolve_path(path)
            with path.open() as path_file:
                for line in path_file:
                    for regex in regexes:
                        if regex.fullmatch(line):
                            return False
            return True

        def system_group_exists(self, group):
            return group in self.system.groups

        def system_user_exists(self, user):
            return user in self.system.users

        def system_path_exists(self, path):
            path = str(get_input_path(path).path)
            return path in self.system.paths or path=='/dev/null'

        def system_program_exists(self, path):
            return shutil.which(path) is not None

        def __getattr__(self, item):
            return self.noop_validator

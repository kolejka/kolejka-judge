# vim:ts=4:sts=4:sw=4:expandtab
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import ExitStack
from copy import deepcopy
from datetime import timedelta
from json import JSONEncoder
assert sys.version_info >= (3, 6)


from kolejka.judge.exceptions import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import CommandBase
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge.systems.base import SystemBase


class LocalSystemValidatorsMixin:
    def file_exists(self, path) -> bool:
        path = self.system.resolve_path(path, self.work_directory)
        return path.is_file() or path == pathlib.Path('/dev/null')

    def directory_exists(self, path) -> bool:
        path = self.system.resolve_path(path, self.work_directory)
        return path.is_dir()

    def program_exists(self, path) -> bool:
        path = self.system.resolve_path(path, self.work_directory)
        return path.is_file() and ( path.stat().st_mode & 0o111 )

    def file_empty(self, path) -> bool:
        path = self.system.resolve_path(path, self.work_directory)
        return not path.is_file() or path.stat().st_size < 1

    def file_does_not_match(self, path, regexes) -> bool:
        path = self.system.resolve_path(path, self.work_directory)
        with path.open() as path_file:
            for line in path_file:
                for regex in regexes:
                    if regex.fullmatch(line):
                        return False
        return True

    def system_path_exists(self, path):
        path = self.system.resolve_path(path, self.work_directory)
        return path.exists()

    def system_program_exists(self, path):
        return shutil.which(path) is not None
        
    def system_user_exists(self, user):
        return True
        
    def system_group_exists(self, group):
        return True


class LocalSystem(SystemBase):
    recognized_limits = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    class LocalStats:
        class MemoryStats:
            def __init__(self, max_usage=None):
                self.max_usage = max_usage

        class CpusStats:
            def __init__(self, usage=None, system=None, user=None):
                self.usage = usage
                self.system = system
                self.user = user

        def __init__(self):
            self.memory = self.MemoryStats()
            self.cpus = {'*': self.CpusStats()}

    class Validators(SystemBase.Validators, LocalSystemValidatorsMixin):
        pass

    class ExecutionStatusEncoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, (pathlib.Path, timedelta, AbstractPath)):
                return str(o)
            return o.__dict__

    def get_superuser(self):
        return os.getuid() == 0

    def update_limits(self, limits):
        return limits

    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits):
        with ExitStack() as stack:
            stats_file = tempfile.NamedTemporaryFile(mode='r', delete=False)
            stats_file.close()
            os.chmod(stats_file.name, 0o666) 
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.write_file(stdout_path, stdout_append))
            stderr_file = stack.enter_context(self.write_file(stderr_path, stderr_append))

            command = ['/usr/bin/time', '-f', 'mem=%M\nreal=%e\nsys=%S\nuser=%U', '-o', stats_file.name] + command
            execution_status = subprocess.run(
                list(map(str, command)),
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
                preexec_fn=self.get_change_user_function(user=user, group=group),
                cwd=work_path,
            )

            stats = self._get_execution_stats(stats_file.name)
            execution_status.stats = LocalSystem.LocalStats()
            execution_status.stats.memory = LocalSystem.LocalStats.MemoryStats(stats['mem'])
            execution_status.stats.cpus['*'] = LocalSystem.LocalStats.CpusStats(
                stats['time']['sys'],
                stats['time']['user'],
                stats['time']['real'],
            )
            os.remove(stats_file.name)

            execution_status.stdout = stdout_path
            execution_status.stderr = stderr_path

            return execution_status

    @staticmethod
    def _get_execution_stats(stats_file_name):
        mem = None
        time = {}
        with open(stats_file_name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('mem='):
                    mem = int(line.strip().split('=')[1]) * 1024
                if line.startswith('real='):
                    time['real'] = timedelta(seconds=float(line.strip().split('=')[1]))
                if line.startswith('user='):
                    time['user'] = timedelta(seconds=float(line.strip().split('=')[1]))
                if line.startswith('sys='):
                    time['sys'] = timedelta(seconds=float(line.strip().split('=')[1]))

        return {'mem': mem, 'time': time}

    @classmethod
    def format_execution_status(cls, status):
        return json.loads(json.dumps(status, cls=cls.ExecutionStatusEncoder))

import json
import os
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
from pathlib import Path
from typing import Optional

from kolejka.judge.commands.base import CommandBase
from kolejka.judge.lazy import DependentExpr
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge.environments.base import ExecutionEnvironment


class LocalExecutionEnvironmentValidatorsMixin:
    def file_exists(self, file) -> bool:
        return os.path.exists(file)

    def program_exists(self, file) -> bool:
        return shutil.which(file) is not None


class LocalComputer(ExecutionEnvironment):
    recognized_limits = []

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

    class Validators(ExecutionEnvironment.Validators, LocalExecutionEnvironmentValidatorsMixin):
        pass

    class ExecutionStatusEncoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, (Path, timedelta)):
                return str(o)
            return o.__dict__

    def run_command(self, command, stdin: Optional[Path], stdout: Optional[Path], stderr: Optional[Path], env,
                    user, group):
        with ExitStack() as stack:
            stats_file = tempfile.NamedTemporaryFile(mode='r', delete=False)
            stats_file.close()
            os.chmod(stats_file.name, 0o666)
            stdin_file = stdin and stack.enter_context(self.get_file_handle(stdin, 'r'))
            stdout_file = stdout and stack.enter_context(self.get_file_handle(stdout, 'w'))
            stderr_file = stderr and stack.enter_context(self.get_file_handle(stderr, 'w'))

            command = ['/usr/bin/time', '-f', 'mem=%M\nreal=%e\nsys=%S\nuser=%U', '-o', stats_file.name] + command
            execution_status = subprocess.run(
                list(map(str, command)),
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=env,
                preexec_fn=self.get_change_user_function(user=user, group=group),
                cwd=self.output_directory,
            )

            stats = self._get_execution_stats(stats_file.name)
            execution_status.stats = LocalComputer.LocalStats()
            execution_status.stats.memory = LocalComputer.LocalStats.MemoryStats(stats['mem'])
            execution_status.stats.cpus['*'] = LocalComputer.LocalStats.CpusStats(
                stats['time']['sys'],
                stats['time']['user'],
                stats['time']['real'],
            )
            os.remove(stats_file.name)

            execution_status.stdout = stdout
            execution_status.stderr = stderr

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

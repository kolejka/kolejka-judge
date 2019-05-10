import json
import os
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from json import JSONEncoder
from pathlib import Path

from commands.base import CommandBase
from tasks.base import Task


class ExecutionEnvironment:
    recognized_limits = []
    variables = {}

    def __init__(self):
        self.limits = {}

    def set_limits(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.recognized_limits:
                print('Unrecognized limit: `{}`, ignoring.'.format(key), file=sys.stderr)

            self.limits[key] = value

    def run_command(self, command, stdin, stdout, stderr, env, name):
        raise NotImplementedError

    def run_step(self, step: CommandBase, name: str):
        step.set_name(name)

        result = None
        configured_correctly, exit_status = step.get_configuration_status()

        if configured_correctly:
            step.verify_prerequisites()

            old_limits = self.limits.copy()
            self.set_limits(**step.get_limits())

            command = step.get_command()
            for i, part in enumerate(command):
                if isinstance(part, DependentExpr):
                    arguments = map(lambda x: self.variables.get(x), part.names)
                    command[i] = part.evaluate(*arguments)

            result = self.run_command(
                command,
                step.get_stdin_file(),
                step.get_stdout_file(),
                step.get_stderr_file(),
                step.get_env(),
                name,
            )
            exit_status = step.verify_postconditions(result)

            self.set_limits(**old_limits)

        return exit_status, result

    def run_task(self, task: Task, name: str):
        return None, task.execute(self)

    def set_variable(self, variable_name, files):
        self.variables[variable_name] = files

    @classmethod
    def format_execution_status(cls, status):
        raise NotImplementedError

    @staticmethod
    def _get_file_handle(file: Path, mode: str):
        file.parent.mkdir(exist_ok=True, parents=True)
        return file.open(mode)


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

    def run_command(self, command, stdin: Path, stdout: Path, stderr: Path, env, name):
        with ExitStack() as stack:
            stats_file = tempfile.NamedTemporaryFile(mode='r', delete=False)
            stats_file.close()
            stdin_file = stdin and stack.enter_context(self._get_file_handle(stdin, 'r'))
            stdout_file = stdout and stack.enter_context(self._get_file_handle(stdout, 'w'))
            stderr_file = stderr and stack.enter_context(self._get_file_handle(stderr, 'w'))

            command = ['/usr/bin/time', '-f', 'mem=%M\nreal=%e\nsys=%S\nuser=%U', '-o', stats_file.name] + command
            execution_status = subprocess.run(
                list(map(str, command)),
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=env,
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
                    mem = '{mem}K'.format(mem=line.strip().split('=')[1])
                if line.startswith('real='):
                    time['real'] = '{time}s'.format(time=line.strip().split('=')[1])
                if line.startswith('user='):
                    time['user'] = '{time}s'.format(time=line.strip().split('=')[1])
                if line.startswith('sys='):
                    time['sys'] = '{time}s'.format(time=line.strip().split('=')[1])

        return {'mem': mem, 'time': time}

    class ExecutionStatusEncoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, Path):
                return str(o)
            return o.__dict__

    @classmethod
    def format_execution_status(cls, status):
        return json.loads(json.dumps(status, cls=cls.ExecutionStatusEncoder))


class KolejkaObserver(ExecutionEnvironment):
    recognized_limits = ['cpus', 'cpus_offset', 'pids', 'memory']

    def run_command(self, command, stdin, stdout, stderr, env, name):
        from kolejka import observer
        from kolejka.common import KolejkaLimits

        with ExitStack() as stack:
            stdin_file = stdin and stack.enter_context(self._get_file_handle(stdin, 'r'))
            stdout_file = stdout and stack.enter_context(self._get_file_handle(stdout, 'w'))
            stderr_file = stderr and stack.enter_context(self._get_file_handle(stderr, 'w'))
            execution_status = observer.run(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=env,
                limits=KolejkaLimits(**self.limits),
            )
            execution_status.stdout = stdout
            execution_status.stderr = stderr

            return execution_status

    class ExecutionStatusEncoder(JSONEncoder):
        def default(self, o):
            from kolejka.common import KolejkaStats
            if isinstance(o, KolejkaStats):
                return o.dump()
            if isinstance(o, Path):
                return str(o)
            return o.__dict__

    @classmethod
    def format_execution_status(cls, status):
        return json.loads(json.dumps(status, cls=cls.ExecutionStatusEncoder))


class DependentExpr:
    def __init__(self, *args, func=None):
        if len(args) > 1 and func is None:
            raise ValueError('Multiple arguments, but no evaluation function given')
        self.names = args
        self.func = func or self.__default_func

    @staticmethod
    def __default_func(x):
        return x

    def evaluate(self, *args):
        return self.func(*args)

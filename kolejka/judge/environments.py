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


class LocalExecutionEnvironmentValidatorsMixin:
    def file_exists(self, file) -> bool:
        return os.path.exists(file)

    def program_exists(self, file) -> bool:
        return shutil.which(file) is not None


class ExecutionEnvironment:
    recognized_limits = []
    variables = {}

    def __init__(self, output_directory=None):
        self.limits = {}
        self.output_directory = Path(output_directory or '.')
        self.validators = self.Validators(self)

    def set_limits(self, **kwargs):
        self.limits = {}
        for key, value in kwargs.items():
            if key not in self.recognized_limits:
                print('Unrecognized limit: `{}`, ignoring.'.format(key), file=sys.stderr)
                continue

            self.limits[key] = value

    def _run_step(self, step, name):
        if isinstance(step, CommandBase):
            return self.run_command_step(step, name=name)
        if isinstance(step, TaskBase):
            return self.run_task_step(step, name=name)

    def run_steps(self, steps):
        result = {}
        for name, step in steps.items():
            exit_status, result[name] = self._run_step(step, name)
            if exit_status is not None:
                return exit_status, result

        return 'OK', result

    def run_command_step(self, step: CommandBase, name: str):
        step.set_name(name)

        result = None
        configured_correctly, exit_status = step.get_configuration_status()

        if configured_correctly:
            step.verify_prerequisites(self)

            old_limits = self.limits.copy()
            self.set_limits(**step.get_limits())

            command = step.get_command()
            for i, part in enumerate(command):
                if isinstance(part, DependentExpr):
                    arguments = map(lambda x: self.variables.get(x), part.names)
                    command[i] = part.evaluate(*arguments)

            env_vars = self.get_env()
            env_vars.update(step.get_env())
            result = self.run_command(
                command,
                step.get_stdin_file(),
                self.get_path(step.get_stdout_file()),
                self.get_path(step.get_stderr_file()),
                env_vars,
                step.get_user(),
                step.get_group(),
            )
            exit_status = step.verify_postconditions(result)

            self.set_limits(**old_limits)

        return exit_status, result

    def run_command(self, command, stdin: Optional[Path], stdout: Optional[Path], stderr: Optional[Path], env,
                    user, group):
        raise NotImplementedError

    def run_task_step(self, task: TaskBase, name: str):
        task.set_name(name)
        task.verify_prerequisites(self)
        return task.execute(self)

    def get_env(self):
        return deepcopy(os.environ)

    def set_variable(self, variable_name, value):
        self.variables[variable_name] = value

    @classmethod
    def format_execution_status(cls, status):
        raise NotImplementedError

    def get_path(self, path: Path):
        return path and self.output_directory / path

    @staticmethod
    def get_file_handle(file: Path, mode: str):
        file.parent.mkdir(exist_ok=True, parents=True)
        return file.open(mode)

    @staticmethod
    def get_change_user_function(user=None, group=None):
        if user is None and group is None:
            return None

        import pwd
        import grp
        uid = pwd.getpwnam(user).pw_uid if user is not None else None
        gid = grp.getgrnam(group).gr_gid if group is not None else None

        def change_user():
            try:
                if gid is not None:
                    os.setgid(gid)
                if uid is not None:
                    os.setuid(uid)
            except OSError:
                pass

        return change_user

    class Validators:
        def __init__(self, environment):
            self.environment = environment

        def noop_validator(self, *args, **kwargs) -> bool:
            return True

        def __getattr__(self, item):
            return self.noop_validator


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


class PsutilEnvironment(ExecutionEnvironment):
    recognized_limits = ['cpu_affinity', 'time', 'memory']

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

    def monitor_process(self, process, execution_status):
        import psutil
        try:
            usage = timedelta(0)
            system = timedelta(0)
            user = timedelta(0)
            memory_max_usage = 0

            process.cpu_affinity(self.limits.get('cpu_affinity', []))
            while True:
                with process.oneshot():
                    usage = max(usage, timedelta(seconds=time.time() - process.create_time()))
                    system = max(system, timedelta(seconds=process.cpu_times().system))
                    user = max(user, timedelta(seconds=process.cpu_times().user))
                    memory_max_usage = max(memory_max_usage, process.memory_info().vms)

                if 'time' in self.limits and usage.total_seconds() > self.limits['time']:
                    process.kill()
                if 'memory' in self.limits and memory_max_usage > self.limits['memory']:
                    process.kill()

                time.sleep(0.1)

        except psutil.NoSuchProcess:
            execution_status.stats.cpus['*'].usage = usage
            execution_status.stats.cpus['*'].system = system
            execution_status.stats.cpus['*'].user = user
            execution_status.stats.memory.max_usage = memory_max_usage

    def run_command(self, command, stdin: Optional[Path], stdout: Optional[Path], stderr: Optional[Path], env,
                    user, group):
        import psutil

        with ExitStack() as stack:
            stdin_file = stdin and stack.enter_context(self.get_file_handle(stdin, 'r'))
            stdout_file = stdout and stack.enter_context(self.get_file_handle(stdout, 'w'))
            stderr_file = stderr and stack.enter_context(self.get_file_handle(stderr, 'w'))

            execution_status = subprocess.CompletedProcess(command, None, stdout, stderr)
            execution_status.stats = PsutilEnvironment.LocalStats()
            process = psutil.Popen(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=env,
                preexec_fn=self.get_change_user_function(user=user, group=group),
            )
            monitoring_thread = threading.Thread(target=self.monitor_process, args=(process, execution_status))
            monitoring_thread.start()
            process.wait()
            monitoring_thread.join()

            execution_status.returncode = process.returncode
            return execution_status

    @classmethod
    def format_execution_status(cls, status):
        return json.loads(json.dumps(status, cls=cls.ExecutionStatusEncoder))


class KolejkaObserver(ExecutionEnvironment):
    recognized_limits = ['cpus', 'cpus_offset', 'pids', 'memory', 'time']

    class Validators(ExecutionEnvironment.Validators, LocalExecutionEnvironmentValidatorsMixin):
        pass

    class ExecutionStatusEncoder(JSONEncoder):
        def default(self, o):
            from kolejka.common import KolejkaStats
            if isinstance(o, KolejkaStats):
                return o.dump()
            if isinstance(o, (Path, timedelta)):
                return str(o)
            return o.__dict__

    def run_command(self, command, stdin: Optional[Path], stdout: Optional[Path], stderr: Optional[Path], env,
                    user, group):
        from kolejka import observer
        from kolejka.common import KolejkaLimits

        with ExitStack() as stack:
            stdin_file = stdin and stack.enter_context(self.get_file_handle(stdin, 'r'))
            stdout_file = stdout and stack.enter_context(self.get_file_handle(stdout, 'w'))
            stderr_file = stderr and stack.enter_context(self.get_file_handle(stderr, 'w'))
            execution_status = observer.run(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=env,
                limits=KolejkaLimits(**self.limits),
                preexec_fn=self.get_change_user_function(user=user, group=group)
            )
            execution_status.stdout = stdout
            execution_status.stderr = stderr

            return execution_status

    @classmethod
    def format_execution_status(cls, status):
        return json.loads(json.dumps(status, cls=cls.ExecutionStatusEncoder))

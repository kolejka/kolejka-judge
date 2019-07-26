# vim:ts=4:sts=4:sw=4:expandtab
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
assert sys.version_info >= (3, 6)


from kolejka.judge.typing import *
from kolejka.judge.commands.base import CommandBase
from kolejka.judge.lazy import DependentExpr
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge.systems.base import SystemBase
from kolejka.judge.systems.local import LocalSystemValidatorsMixin


class PsutilSystem(SystemBase):
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

    class Validators(SystemBase.Validators, LocalSystemValidatorsMixin):
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

    def run_command(self, command, stdin: Optional[Path], stdout: Optional[Path], stderr: Optional[Path], environment,
                    user, group):
        import psutil

        with ExitStack() as stack:
            stdin_file = stdin and stack.enter_context(self.get_file_handle(stdin, 'r'))
            stdout_file = stdout and stack.enter_context(self.get_file_handle(stdout, 'w'))
            stderr_file = stderr and stack.enter_context(self.get_file_handle(stderr, 'w'))

            execution_status = subprocess.CompletedProcess(command, None, stdout, stderr)
            execution_status.stats = PsutilSystem.LocalStats()
            process = psutil.Popen(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                environment=environment,
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

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


class ObserverSystem(SystemBase):
    recognized_limits = ['cpus', 'cpus_offset', 'pids', 'memory', 'time']

    class Validators(SystemBase.Validators, LocalSystemValidatorsMixin):
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
                preexec_fn=self.get_change_user_function(user=user, group=group),
                cwd=self.output_directory,
            )
            execution_status.stdout = stdout
            execution_status.stderr = stderr

            return execution_status

    @classmethod
    def format_execution_status(cls, status):
        return json.loads(json.dumps(status, cls=cls.ExecutionStatusEncoder))

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
                self.get_path(step.get_stdin_file()),
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
        if os.getuid() != 0:
            return None
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

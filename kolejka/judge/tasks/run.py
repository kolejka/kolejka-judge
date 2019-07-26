# vim:ts=4:sts=4:sw=4:expandtab
import glob
import shlex
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import *
from kolejka.judge.tasks.base import TaskBase


__all__ = [ 'ExecutableTask', 'SolutionExecutableTask', 'ToolExecutableTask', ]
def __dir__():
    return __all__

class ExecutableTask(TaskBase):
    @default_kwargs
    def __init__(self, executable, executable_arguments=None, stdin=None, stdout=None, stdout_append=None, stderr=None, stderr_append=None, **kwargs):
        super().__init__(**kwargs)
        self._executable = str(executable)
        self._executable_arguments = executable_arguments or []
        self._stdin = stdin
        self._stdout = stdout
        self._stdout_append = stdout_append
        self._stderr = stderr
        self._stderr_append = stderr_append

    @property
    def executable(self) -> OutputPath:
        return self.get_executable()
    def get_executable(self):
        return self._executable

    @property
    def executable_arguments(self) -> List[Resolvable]:
        return self.get_executable_arguments()
    def get_executable_arguments(self):
        return self._executable_arguments

    @property
    def stdin(self) -> Optional[AbstractPath]:
        return self.get_stdin()
    def get_stdin(self):
        return self._stdin

    @property
    def stdout(self) -> Optional[OutputPath]:
        return self.get_stdout()
    def get_stdout(self):
        return self._stdout

    @property
    def stdout_append(self) -> bool:
        return self.get_stdout_append()
    def get_stdout_append(self):
        return self._stdout_append

    @property
    def stderr(self) -> Optional[OutputPath]:
        return self.get_stderr()
    def get_stderr(self):
        return self._stderr

    @property
    def stderr_append(self) -> bool:
        return self.get_stderr_append()
    def get_stderr_append(self):
        return self._stderr_append

    def get_command_kwargs(self):
        kwargs = super().get_command_kwargs()
        if self.stdin is not None:
            kwargs['stdin'] = self.stdin
        if self.stdout is not None:
            kwargs['stdout'] = self.stdout
        if self.stdout_append is not None:
            kwargs['stdout_append'] = self.stdout_append
        if self.stderr is not None:
            kwargs['stderr'] = self.stderr
        if self.stderr_append is not None:
            kwargs['stderr_append'] = self.stderr_append
        return kwargs

    def execute(self):
        status = None
        status = status or self.run_command('run', ExecutableCommand, executable=self.executable, executable_arguments=self.executable_arguments)
        return status, self.result


class SolutionExecutableTask(ExecutableTask):
    DEFAULT_EXECUTABLE='solution/run'
    DEFAULT_ANSWER_PATH='test/answer'
    DEFAULT_RESULT_ON_ERROR='RTE'
#TODO:    DEFAULT_RESULT_ON_TIME='TLE'
#TODO:    DEFAULT_RESULT_ON_MEMORY='MEM'
    @default_kwargs
    def __init__(self, input_path=None, answer_path=None, **kwargs):
        super().__init__(**kwargs)
        self.input_path = input_path and get_output_path(input_path) or super().get_stdin()
        self.answer_path = answer_path and get_output_path(answer_path) or super().get_stdout()
    def get_stdin(self):
        return self.input_path
    def get_stdout(self):
        return self.answer_path

class ToolExecutableTask(ExecutableTask):
    DEFAULT_EXECUTABLE='tool/{tool_name}'
    DEFAULT_RESULT_ON_ERROR='INT'
    @default_kwargs
    def __init__(self, tool_name, **kwargs):
        if isinstance(kwargs['executable'], str):
            kwargs['executable'] = kwargs['executable'].format(tool_name=tool_name)
        super().__init__(**kwargs)

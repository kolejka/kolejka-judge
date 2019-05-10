from pathlib import Path

from commands.base import CommandBase
from validators import ProgramExistsPrerequisite, FileExistsPrerequisite, ExitCodePostcondition


class Run(CommandBase):
    def __init__(self, executable, cmdline_options=None, stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(**kwargs)
        self.executable = executable
        self.cmdline_options = cmdline_options or []
        self.stdin = stdin and Path(stdin)
        self.stdout = stdout and Path(stdout)
        self.stderr = stderr and Path(stderr)

    def get_stdin_file(self):
        return self.stdin

    def get_stdout_file(self):
        return self.stdout or super().get_stdout_file()

    def get_stderr_file(self):
        return self.stderr or super().get_stderr_file()

    def get_command(self):
        return [self.executable] + self.cmdline_options

    def prerequisites(self):
        prerequisites = [ProgramExistsPrerequisite(self.executable)]
        if self.stdin is not None:
            prerequisites.append(FileExistsPrerequisite(self.stdin))
        return prerequisites


class RunSolution(Run):
    def __init__(self, executable='./a.out', cmdline_options=None, stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(executable=executable, cmdline_options=cmdline_options,
                         stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'RTE')
        ]

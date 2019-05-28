from kolejka.judge.commands.mixins import SolutionMixin
from kolejka.judge.commands.run.base import Run
from kolejka.judge.validators import ExitCodePostcondition, FileExistsPrerequisite


class RunCSharp(Run):
    def __init__(self, file, interpreter_options=None, cmdline_options=None,
                 stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(executable='mono', cmdline_options=cmdline_options,
                         stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
        self.file = file
        self.interpreter_options = interpreter_options or []

    def prerequisites(self):
        prerequisites = super().prerequisites()
        prerequisites.append(FileExistsPrerequisite(self.file))
        return prerequisites

    def get_command(self):
        return [self.executable] + self.interpreter_options + [self.file] + self.cmdline_options


class RunCSharpSolution(SolutionMixin, RunCSharp):
    def postconditions(self):
        return super().postconditions() + [
            (ExitCodePostcondition(), 'RTE')
        ]

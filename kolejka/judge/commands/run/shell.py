from kolejka.judge.commands.mixins import SolutionMixin
from kolejka.judge.commands.run.base import Run
from kolejka.judge.validators import ExitCodePostcondition


class RunShell(Run):
    pass


class RunShellSolution(SolutionMixin, RunShell):
    def postconditions(self):
        return super().postconditions() + [
            (ExitCodePostcondition(), 'RTE')
        ]

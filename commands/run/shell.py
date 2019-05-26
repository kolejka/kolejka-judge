from commands.mixins import SolutionMixin
from commands.run.base import Run
from validators import ExitCodePostcondition


class RunShell(Run):
    pass


class RunShellSolution(SolutionMixin, RunShell):
    def postconditions(self):
        return super().postconditions() + [
            (ExitCodePostcondition(), 'RTE')
        ]

from kolejka.judge.commands.mixins import SolutionMixin
from kolejka.judge.commands.run.base import Run


class RunShell(Run):
    pass


class RunShellSolution(SolutionMixin, RunShell):
    pass

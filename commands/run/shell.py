from commands.run.base import Run
from validators import ExitCodePostcondition


class RunShell(Run):
    pass


class RunShellSolution(RunShell):
    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'RTE')
        ]

from kolejka.judge.commands.mixins import SolutionMixin
from kolejka.judge.commands.run.base import Run
from kolejka.judge.validators import FileExistsPrerequisite


class RunPython(Run):
    python_interpreter = 'python'

    def __init__(self, python_file, interpreter_options=None, cmdline_options=None,
                 stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(executable=self.python_interpreter, cmdline_options=cmdline_options,
                         stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
        self.python_file = python_file
        self.interpreter_options = interpreter_options

    def prerequisites(self):
        prerequisites = super().prerequisites()
        prerequisites.append(FileExistsPrerequisite(self.python_file))
        return prerequisites

    def get_command(self):
        return [self.executable] + self.interpreter_options + [self.python_file] + self.cmdline_options


class RunPython2(RunPython):
    python_interpreter = 'python2'


class RunPython3(RunPython):
    python_interpreter = 'python3'


class RunPythonSolution(SolutionMixin, RunPython):
    pass


class RunPython2Solution(RunPython2, RunPythonSolution):
    pass


class RunPython3Solution(RunPython3, RunPythonSolution):
    pass

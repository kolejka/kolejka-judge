from kolejka.judge.commands.mixins import SolutionMixin
from kolejka.judge.commands.run.base import Run
from kolejka.judge.validators import FileExistsPrerequisite


class RunJavaClass(Run):
    def __init__(self, class_name, interpreter_options=None, cmdline_options=None,
                 stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(executable='java', cmdline_options=cmdline_options,
                         stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
        self.class_name = class_name
        self.interpreter_options = interpreter_options or []

    def prerequisites(self):
        prerequisites = super().prerequisites()
        prerequisites.append(FileExistsPrerequisite(self.class_name + '.class'))
        return prerequisites

    def get_command(self):
        return [self.executable] + self.interpreter_options + [self.class_name] + self.cmdline_options


class RunJar(Run):
    def __init__(self, jar_file='archive.jar', interpreter_options=None, cmdline_options=None,
                 stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(executable='java', cmdline_options=cmdline_options,
                         stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
        self.jar_file = jar_file
        self.interpreter_options = interpreter_options or []

    def prerequisites(self):
        prerequisites = super().prerequisites()
        prerequisites.append(FileExistsPrerequisite(self.jar_file))
        return prerequisites

    def get_command(self):
        return [self.executable] + self.interpreter_options + ['-jar', self.jar_file] + self.cmdline_options


class RunJavaClassSolution(SolutionMixin, RunJavaClass):
    pass


class RunJarSolution(SolutionMixin, RunJar):
    pass


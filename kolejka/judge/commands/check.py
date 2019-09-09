# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'DiffCommand', 'CheckerCommand', ]
def __dir__():
    return __all__


class DiffCommand(ProgramCommand):
    DEFAULT_PROGRAM='diff'
    DEFAULT_SAFE=True
    @default_kwargs
    def __init__(self, path_a, path_b, case_sensitive=True, space_sensitive=False, **kwargs):
        super().__init__(**kwargs)
        self.path_a = get_output_path(path_a)
        self.path_b = get_output_path(path_b)
        self.case_sensitive = bool(case_sensitive)
        self.space_sensitive = bool(space_sensitive)

    #TODO: quiet/verbose
    def get_program_arguments(self):
        args = []
        args += [ '-q', ]
        if not self.case_sensitive:
            args += [ '-i', ]
        if not self.space_sensitive:
            args += [ '-w', '-B', ]
        args += [ self.path_a, self.path_b, ]
        return args 

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.path_a),
            FileExistsPrerequirement(self.path_b),
        ]


class CheckerCommand(ExecutableCommand):
    DEFAULT_SAFE=True
    @default_kwargs
    def __init__(self, input_path=None, hint_path=None, answer_path=None, **kwargs):
        super().__init__(**kwargs)
        self.input_path = input_path and get_output_path(input_path)
        self.hint_path = hint_path and get_output_path(hint_path)
        self.answer_path = answer_path and get_output_path(answer_path)

    def get_executable_arguments(self):
        return [ self.input_path, self.hint_path, self.answer_path ]

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.input_path),
            FileExistsPrerequirement(self.hint_path),
            FileExistsPrerequirement(self.answer_path),
        ]

# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'MakeCommand', 'CMakeCommand', ]
def __dir__():
    return __all__


class MakeCommand(ProgramCommand):
    DEFAULT_PROGRAM='make'
    @default_kwargs
    def __init__(self, build_directory=None, build_target=None, makefile=None, **kwargs):
        super().__init__(**kwargs)
        self.build_directory = build_directory and get_output_path(build_directory) or super().get_work_directory()
        self.build_target = build_target and str(build_target) or None
        self.makefile = get_relative_path(makefile or 'Makefile')

    def get_work_directory(self):
        return self.build_directory

    def get_program_arguments(self):
        args = []
        if not self.verbose:
            args += [ '--silent', ]
        args += [ '--makefile', self.makefile, ]
        if self.build_target:
            args += [ self.build_target, ]
        return args

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.makefile),
        ]


class CMakeCommand(ProgramCommand):
    DEFAULT_PROGRAM='cmake'
    @default_kwargs
    def __init__(self, source_directory=None, build_directory=None, **kwargs):
        super().__init__(**kwargs)
        self.build_directory = build_directory and get_output_path(build_directory) or super().get_work_directory()
        self.source_directory = source_directory and get_output_path(source_directory) or self.build_directory
        self.cmakelists = self.source_directory / 'CMakeLists.txt'

    def get_work_directory(self):
        return self.build_directory

    def get_program_arguments(self):
        return [ self.source_directory, ]

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.cmakelists),
        ]

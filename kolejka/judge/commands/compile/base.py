# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'CompileCommand', ]
def __dir__():
    return __all__


class CompileCommand(ProgramCommand):
    @default_kwargs
    def __init__(self, build_directory=None, build_arguments=None, build_target=None, source_files=None, libraries=None, **kwargs):
        super().__init__(**kwargs)
        self._build_directory = build_directory and get_output_path(build_directory) or super().get_work_directory()
        self._build_arguments = build_arguments or []
        self._build_target = build_target and get_relative_path(build_target)
        self._source_files = [ get_output_path(source_file) for source_file in ( source_files or [] ) ]
        self._libraries = libraries or []

    @property
    def build_directory(self):
        return self.get_build_directory()
    def get_build_directory(self):
        return self._build_directory

    @property
    def build_arguments(self):
        return self.get_build_arguments()
    def get_build_arguments(self):
        return self._build_arguments

    @property
    def build_target(self):
        return self.get_build_target()
    def get_build_target(self):
        return self._build_target

    @property
    def source_files(self):
        return self.get_source_files()
    def get_source_files(self):
        return self._source_files

    @property
    def libraries(self):
        return self.get_libraries()
    def get_libraries(self):
        return self._libraries

    def get_library_arguments(self, library):
        return [ library, ]

    def get_source_arguments(self, source):
        return [ source, ]

    def get_target_arguments(self, target):
        return [ target, ]

    @property
    def execution_command(self):
        return self.get_execution_command()
    def get_execution_command(self):
        return [ self.build_directory / self.build_target ]

    def get_program_arguments(self):
        args = []
        args += super().get_program_arguments()
        args += self.build_arguments
        for source in self.source_files:
            args += self.get_source_arguments(source)
        for library in self.libraries:
            args += self.get_library_arguments(library)
        if self.build_target:
            args += self.get_target_arguments(self.build_target)
        return args

    def get_work_directory(self):
        return self.build_directory

    def get_prerequirements(self):
        return super().get_prerequirements() + [ FileExistsPrerequirement(source_file) for source_file in self.source_files ]

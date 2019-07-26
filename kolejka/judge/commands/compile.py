# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'GCCCommand', 'LDCommand', 'GXXCommand', 'GCCGoCommand', 'NasmCommand', 'MCSCommand', 'GHCCommand' ]
def __dir__():
    return __all__


class CompileCommand(ProgramCommand):
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
        args = super().get_program_arguments()
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


class GCCCommand(CompileCommand):
    DEFAULT_PROGRAM='gcc'
    DEFAULT_BUILD_ARGUMENTS = [ '-Wall', '-O2', ]
    DEFAULT_VERBOSE_ARGUMENTS = [ '-Wextra', '-Wpedantic', ]
    @default_kwargs
    def __init__(self, static=False, version=None, standard=None, **kwargs):
        super().__init__(**kwargs)
        self._static = bool(static)
        self._version = version and str(version)
        self._standard = standard and str(standard)
    @property
    def static(self):
        return self.get_static()
    def get_static(self):
        return self._static
    @property
    def version(self):
        return self.get_version()
    def get_version(self):
        return self._version
    @property
    def standard(self):
        return self.get_standard()
    def get_standard(self):
        return self._standard
    
    def get_program(self):
        program = super().get_program()
        if self.version:
            program = program+'-'+str(self.version)
        return program

    def get_build_arguments(self):
        arguments = []
        if self.standard:
            arguments += [ '-std='+self.standard, ]
        if self.static:
            arguments += [ '-static', ]
        return arguments + super().get_build_arguments()
    def get_library_arguments(self, library):
        return [ '-l' + library, ]
    def get_target_arguments(self, target):
        return [ '-o', target, ]
    def get_build_target(self):
        return super().get_build_target() or get_relative_path('a.out')

class LDCommand(GCCCommand):
    DEFAULT_PROGRAM='ld'
    DEFAULT_BUILD_ARGUMENTS = [ '-Wall', ]
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GXXCommand(GCCCommand):
    DEFAULT_PROGRAM='g++'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GCCGoCommand(GCCCommand):
    DEFAULT_PROGRAM='gccgo'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NasmCommand(CompileCommand):
    DEFAULT_PROGRAM='nasm'
    DEFAULT_BUILD_ARGUMENTS = [ '-felf64' ]
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MCSCommand(CompileCommand):
    DEFAULT_PROGRAM='mcs'
    DEFAULT_BUILD_ARGUMENTS = [ '-t:exe' ]
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_target_arguments(self, target):
        return [ [ '-out:', target, ], ]
    def get_execution_command(self):
        return [ 'mono', self.build_target ]
    def get_build_target(self):
        return super().get_build_target() or get_relative_path('main.exe')


class GHCCommand(CompileCommand):
    DEFAULT_PROGRAM='ghc'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

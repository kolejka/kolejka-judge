# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'GCCCommand', 'LDCommand', 'GXXCommand', 'GCCGoCommand', ]
def __dir__():
    return __all__


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
        args = []
        if self.standard:
            args += [ '-std='+self.standard, ]
        if self.static:
            args += [ '-static', ]
        return args + super().get_build_arguments()
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

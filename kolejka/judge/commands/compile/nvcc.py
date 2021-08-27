# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'NVCCCommand' ]
def __dir__():
    return __all__


class NVCCCommand(CompileCommand):
    DEFAULT_PROGRAM='nvcc'
    DEFAULT_BUILD_ARGUMENTS = [ '-O3', '-extended-lambda', ]
    DEFAULT_VERBOSE_ARGUMENTS = [ ]
    @default_kwargs
    def __init__(self, static=False, standard=None, architecture=None, **kwargs):
        super().__init__(**kwargs)
        self._static = bool(static)
        self._standard = standard and str(standard)
        self._architecture = architecture and str(architecture)
    @property
    def static(self):
        return self.get_static()
    def get_static(self):
        return self._static
    @property
    def standard(self):
        return self.get_standard()
    def get_standard(self):
        return self._standard
    @property
    def architecture(self):
        return self.get_architecture()
    def get_architecture(self):
        return self._architecture
    
    def get_build_arguments(self):
        args = []
        if self.standard:
            args += [ '-std='+self.standard, ]
        if self.static:
            args += [ '-static', ]
        if self.architecture:
            args += [ '-arch='+self.architecture, ]
        return args + super().get_build_arguments()
    def get_library_arguments(self, library):
        return [ '-l' + library, ]
    def get_target_arguments(self, target):
        return [ '-o', target, ]
    def get_build_target(self):
        return super().get_build_target() or get_relative_path('a.out')

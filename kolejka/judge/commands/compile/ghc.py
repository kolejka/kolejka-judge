# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'GHCCommand', ]
def __dir__():
    return __all__


class GHCCommand(CompileCommand):
    DEFAULT_PROGRAM='ghc'
    DEFAULT_BUILD_ARGUMENTS = [ '--make', '-O2', ]
    @default_kwargs
    def __init__(self, static=False, **kwargs):
        super().__init__(**kwargs)
        self._static = bool(static)
    @property
    def static(self):
        return self.get_static()
    def get_static(self):
        return self._static
    def get_build_arguments(self):
        args = []
        if self.static:
            args += [ '-static', ]
        return args + super().get_build_arguments()
    def get_library_arguments(self, library):
        return [ '-l' + library, ]
    def get_target_arguments(self, target):
        return [ '-o', target, ]
    def get_build_target(self):
        return super().get_build_target() or get_relative_path('a.out')

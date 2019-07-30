# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'MCSCommand', ]
def __dir__():
    return __all__


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

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
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

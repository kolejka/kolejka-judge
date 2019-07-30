# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'NasmCommand', ]
def __dir__():
    return __all__


class NasmCommand(CompileCommand):
    DEFAULT_PROGRAM='nasm'
    DEFAULT_BUILD_ARGUMENTS = [ '-felf64' ]
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

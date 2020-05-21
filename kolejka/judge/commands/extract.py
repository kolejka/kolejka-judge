# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'Un7zCommand', 'UnzipCommand', 'UnrarCommand', 'UntarCommand', ]
def __dir__():
    return __all__


class ExtractCommand(ProgramCommand):
    DEFAULT_SAFE=True
    @default_kwargs
    def __init__(self, source, target, **kwargs):
        super().__init__(**kwargs)
        self._source = get_output_path(source)
        self._target = get_output_path(target)

    @property
    def source(self):
        return self.get_source()
    def get_source(self):
        return self._source

    @property
    def target(self):
        return self.get_target()
    def get_target(self):
        return self._target

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.source),
            DirectoryExistsPrerequirement(self.target),
        ]


class Un7zCommand(ExtractCommand):
    DEFAULT_PROGRAM='7z'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_program_arguments(self):
        return [ 'x', '-y', '-aoa', '-bso0', '-bse2', '-bsp0', '-bb0', '-bd', ['-o', self.target], self.source ]
    #TODO: quiet/verbose

class UnzipCommand(Un7zCommand):
    pass

class UnrarCommand(Un7zCommand):
    pass

class UntarCommand(ExtractCommand):
    DEFAULT_PROGRAM='tar'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_program_arguments(self):
        return [ '--extract', '-f', self.source, '--force-local', '--auto-compress', '--overwrite', '--no-same-owner', '--no-acls', '--no-selinux', '--no-xattrs', '-C', self.target ]
    #TODO: quiet/verbose

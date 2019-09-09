# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'ZipCommand' ]
def __dir__():
    return __all__


class CompressCommand(ProgramCommand):
    DEFAULT_SAFE=True
    @default_kwargs
    def __init__(self, sources, target, **kwargs):
        super().__init__(**kwargs)
        self._sources = [ get_output_path(source) for source in sources ]
        self._target = get_output_path(target)

    @property
    def sources(self):
        return self.get_sources()
    def get_sources(self):
        return self._sources

    @property
    def target(self):
        return self.get_target()
    def get_target(self):
        return self._target

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(source) for source in self.sources
        ]


class ZipCommand(CompressCommand):
    DEFAULT_PROGRAM='zip'
    DEFAULT_STORE_DIRECTORIES=True
    @default_kwargs
    def __init__(self, store_directories, **kwargs):
        super().__init__(**kwargs)
        self.store_directories = bool(store_directories)

    def get_program_arguments(self):
        arguments = []
        if not self.store_directories:
            arguments += [ '--junk-paths' ]
        arguments += [ '--no-wild', '--symlinks', '-9', self.target, ] + self.sources
        return arguments
    #TODO: quiet/verbose

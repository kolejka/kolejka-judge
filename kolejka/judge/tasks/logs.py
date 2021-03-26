# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import *


__all__ = [ 'CollectLogsTask' ]
def __dir__():
    return __all__


class CollectLogsTask(TaskBase):
    DEFAULT_SOURCE=config.LOG
    DEFAULT_TARGET=config.COLLECTED_LOG
    DEFAULT_OBLIGATORY=True
    @default_kwargs
    def __init__(self, source, target, **kwargs):
        super().__init__(**kwargs)
        self.source = get_output_path(source)
        self.target = get_output_path(target)

    @property
    def sources(self):
        return self.get_sources()

    def file_empty(self, path):
        return self.system.validators.file_empty(self.resolve_path(path))

    def get_sources(self):
        return [ path for path in self.find_files(self.source) if not self.file_empty(path) ]

    def execute(self):
        self.set_result(self.run_command('zip', ZipCommand, target=self.target, sources=self.sources, store_directories=False))
        if not self.status:
            self.set_result(name='logs', value=self.resolve_path(self.target))
        return self.result

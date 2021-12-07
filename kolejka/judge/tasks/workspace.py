# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.typing import *
from kolejka.judge.tasks.system import *


__all__ = [ 'WorkspacePrepareTask', ]
def __dir__():
    return __all__

class WorkspacePrepareTask(DirectoryAddTask):
    DEFAULT_DIRECTORY=config.WORKSPACE
    DEFAULT_USER_NAME=config.USER_TEST
    DEFAULT_GROUP_NAME=config.GROUP_ALL
    DEFAULT_MODE=0o2770
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

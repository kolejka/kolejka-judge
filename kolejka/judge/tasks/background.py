# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge.tasks.base import *
from kolejka.judge.typing import *


__all__ = [ 'ClearBackgroundTask' ]
def __dir__():
    return __all__

class ClearBackgroundTask(TaskBase):
    DEFAULT_OBLIGATORY=True
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def execute(self):
        self.system.clear_background()
        return self.result

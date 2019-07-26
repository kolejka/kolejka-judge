# vim:ts=4:sts=4:sw=4:expandtab
import glob
import shlex
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.check import *
from kolejka.judge.tasks.base import TaskBase


__all__ = [ 'AnswerHintDiffTask', ]
def __dir__():
    return __all__


class AnswerHintDiffTask(TaskBase):
    DEFAULT_RESULT_ON_ERROR='ANS'
    @default_kwargs
    def __init__(self, hint_path, answer_path, case_sensitive=True, space_sensitive=False, **kwargs):
        super().__init__(**kwargs)
        self.hint_path = get_output_path(hint_path)
        self.answer_path = get_output_path(answer_path)
        self.case_sensitive = bool(case_sensitive)
        self.space_sensitive = bool(space_sensitive)

    def execute(self):
        status = self.run_command('diff', DiffCommand, path_a=self.hint_path, path_b=self.answer_path, case_sensitive=self.case_sensitive, space_sensitive=self.space_sensitive)
        return status, self.result

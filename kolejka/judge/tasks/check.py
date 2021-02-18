# vim:ts=4:sts=4:sw=4:expandtab
import glob
import shlex


from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import TaskBase


__all__ = [ 'AnswerHintDiffTask', 'AnswerHintTableDiffTask' ]
def __dir__():
    return __all__


class AnswerHintDiffTask(TaskBase):
    DEFAULT_RESULT_ON_ERROR='ANS'
    DEFAULT_ANSWER_PATH=config.TEST_ANSWER
    DEFAULT_CASE_SENSITIVE=True
    DEFAULT_SPACE_SENSITIVE=False
    @default_kwargs
    def __init__(self, hint_path, answer_path, case_sensitive, space_sensitive, **kwargs):
        super().__init__(**kwargs)
        self.hint_path = get_output_path(hint_path)
        self.answer_path = get_output_path(answer_path)
        self.case_sensitive = bool(case_sensitive)
        self.space_sensitive = bool(space_sensitive)

    def execute(self):
        self.set_result(self.run_command('diff', DiffCommand, path_a=self.hint_path, path_b=self.answer_path, case_sensitive=self.case_sensitive, space_sensitive=self.space_sensitive))
        return self.result

class AnswerHintTableDiffTask(TaskBase):
    DEFAULT_RESULT_ON_ERROR='ANS'
    DEFAULT_ANSWER_PATH=config.TEST_ANSWER
    DEFAULT_CASE_SENSITIVE=True
    DEFAULT_SPACE_SENSITIVE=False
    DEFAULT_ROW_DELIMETER=False
    DEFAULT_COLUMN_DELIMETER=False
    DEFAULT_ROW_SORT=False
    DEFAULT_COLUMN_SORT=False
    DEFAULT_EMPTY_ROW=False
    DEFAULT_EMPTY_COLUMN=False
    @default_kwargs
    def __init__(self, hint_path, answer_path, case_sensitive, space_sensitive, row_sort, column_sort, row_delimeter, column_delimeter, empty_row, empty_column, **kwargs):
        super().__init__(**kwargs)
        self.hint_path = get_output_path(hint_path)
        self.answer_path = get_output_path(answer_path)
        self.case_sensitive = bool(case_sensitive)
        self.space_sensitive = bool(space_sensitive)
        self.row_delimeter = row_delimeter or False
        self.row_sort = bool(row_sort) and self.row_delimeter
        self.empty_row = bool(empty_row)
        self.column_delimeter = self.row_delimeter and column_delimeter or False
        self.column_sort = bool(column_sort) and self.column_delimeter
        self.empty_column = bool(empty_column)

    def apply(self, data, operator):
        if data is None:
            return None
        if isinstance(data, str):
            return operator(data)
        if isinstance(data, (list, tuple)):
            return [ self.apply(e, operator) for e in data ]

    def represent(self, path):
        data = self.resolve_path(path).open().read()
        if not self.case_sensitive:
            data = data.lower()
        if self.row_delimeter:
            data = re.split(self.row_delimeter, data, flags=re.MULTILINE|re.DOTALL)
            if self.column_delimeter:
                data = [ re.split(self.column_delimeter, row, flags=re.MULTILINE|re.DOTALL) for row in data ]
        if not self.space_sensitive:
            data = self.apply(data, lambda e : re.sub(r'\s+',' ', e.strip()))
        if self.row_delimeter:
            if self.column_delimeter:
                if not self.empty_column:
                    data = [ [ cell for cell in row if cell ] for row in data ]
                if self.column_sort:
                    data = [ sorted(row) for row in data ]
            if not self.empty_row:
                data = [ row for row in data if row ]
            if self.row_sort:
                data = sorted(data)
        return data

    def execute(self):
        if self.represent(self.hint_path) != self.represent(self.answer_path):
            self.set_result(self.result_on_error)
        return self.result

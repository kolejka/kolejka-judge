import glob
import itertools
from functools import partial

from kolejka.judge.typing import *
from kolejka.judge.tasks.base import TaskBase


class ListFiles(TaskBase):
    def __init__(self, *args, variable_name):
        self.files = list(args)
        self.variable_name = variable_name

    def execute(self, environment) -> Tuple[Optional[str], Optional[object]]:
        files = list(itertools.chain.from_iterable(map(partial(glob.glob, recursive=True), self.files)))
        environment.set_variable(self.variable_name, files)

        return None, None

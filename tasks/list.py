import glob
import itertools
from functools import partial

from tasks.base import Task


class ListFilesTask(Task):
    def __init__(self, *args, variable_name):
        self.files = list(args)
        self.variable_name = variable_name

    def execute(self, environment):
        files = list(itertools.chain.from_iterable(map(partial(glob.glob, recursive=True), self.files)))
        environment.set_variable(self.variable_name, files)

        return {}

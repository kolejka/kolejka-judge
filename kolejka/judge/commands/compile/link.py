import glob
import itertools
from functools import partial

from kolejka.judge.commands.base import CommandBase
from kolejka.judge.validators import FileExistsPrerequisite, NonEmptyFilesListPrerequisite, ExitCodePostcondition


class Link(CommandBase):
    def __init__(self, *args, output='a.out', **kwargs):
        super().__init__(**kwargs)
        self.files = list(args)
        self.output = output

    def get_command(self):
        return ['ld'] + self.files + ['-o', self.output]

    def prerequisites(self):
        self.files = list(itertools.chain.from_iterable(map(partial(glob.glob, recursive=True), self.files)))
        files_prerequisites = list(map(FileExistsPrerequisite, self.files))
        non_empty_files = [NonEmptyFilesListPrerequisite(self.files)]
        return [*files_prerequisites, *non_empty_files]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]

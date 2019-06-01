import glob
import itertools
from functools import partial
from typing import List

from kolejka.judge.commands.base import CommandBase
from kolejka.judge.validators import ProgramExistsPrerequisite, FileExistsPrerequisite, ExitCodePostcondition, \
    NonEmptyListPrerequisite


class CompileBase(CommandBase):
    def __init__(self, compiler, *args: str, compilation_options: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.compiler = compiler
        self.compilation_options = compilation_options or []
        self.files = list(args)

    def get_command(self):
        return [self.compiler] + self.compilation_options + self.files

    def prerequisites(self):
        self.files = list(itertools.chain.from_iterable(map(partial(glob.glob, recursive=True), self.files)))
        compiler_prerequisites = [ProgramExistsPrerequisite(self.compiler)]
        source_files_prerequisites = list(map(FileExistsPrerequisite, self.files))
        non_empty_sources = [NonEmptyListPrerequisite(self.files)]
        return [*compiler_prerequisites, *source_files_prerequisites, *non_empty_sources]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]

import glob
import itertools
from functools import partial
from typing import List

from commands.base import CommandBase
from commands.compile.base import CompileBase
from validators import ProgramExistsPrerequisite, FileExistsPrerequisite, ExitCodePostcondition


class CompileJava(CompileBase):
    def __init__(self, *args: str, compiler='javac', compilation_options: List[str] = None, **kwargs):
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)


class CreateJar(CommandBase):
    executable = 'jar'

    def __init__(self, *args: str, output_file='archive.jar', manifest=None, entrypoint=None, options: List[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.output_file = output_file
        self.manifest = manifest
        self.entrypoint = entrypoint
        self.options = options
        self.files = list(args)

    def prerequisites(self):
        self.files = list(itertools.chain.from_iterable(map(partial(glob.glob, recursive=True), self.files)))
        source_files_prerequisites = list(map(FileExistsPrerequisite, self.files))
        return [ProgramExistsPrerequisite(self.executable)] + source_files_prerequisites

    def get_command(self):
        flags = 'cf'
        flags_command = [self.output_file]
        if self.manifest is not None:
            flags += 'm'
            flags_command.append(self.manifest)
        if self.entrypoint is not None:
            flags += 'e'
            flags_command.append(self.entrypoint)

        return [self.executable, flags] + flags_command + self.files

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]

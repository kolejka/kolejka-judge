from commands.base import CommandBase
from validators import ExitCodePostcondition, FileExistsPrerequisite


class Diff(CommandBase):
    def __init__(self, file1='out', file2='wzo', **kwargs):
        super().__init__(**kwargs)
        self.file1 = file1
        self.file2 = file2

    def get_command(self):
        return ['diff', '-Z', self.file1, self.file2]

    def prerequisites(self):
        return [
            FileExistsPrerequisite(self.file1),
            FileExistsPrerequisite(self.file2),
        ]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'ANS')
        ]

    def input_files(self):
        return [self.file1, self.file2]

    def output_files(self):
        return []

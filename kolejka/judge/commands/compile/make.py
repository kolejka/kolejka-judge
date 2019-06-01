from kolejka.judge.commands.base import CommandBase
from kolejka.judge.validators import ExitCodePostcondition, ProgramExistsPrerequisite


class Make(CommandBase):
    executable = 'make'

    def __init__(self, target=None, build_dir='.', **kwargs):
        super().__init__(**kwargs)
        self.build_dir = build_dir
        self.target = target

    def get_command(self):
        target = [] if self.target is None else [self.target]
        return [self.executable, '-C', self.build_dir] + target

    def prerequisites(self):
        return [ProgramExistsPrerequisite(self.executable)]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]


class CMake(CommandBase):
    executable = 'cmake'

    def __init__(self, source_dir='.', build_dir='build', **kwargs):
        super().__init__(**kwargs)
        self.source_dir = source_dir
        self.build_dir = build_dir

    def get_command(self):
        # INFO: -S replaces -H in newer versions
        return [self.executable, '-B{}'.format(self.build_dir), '-H{}'.format(self.source_dir)]

    def prerequisites(self):
        return [ProgramExistsPrerequisite(self.executable)]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]

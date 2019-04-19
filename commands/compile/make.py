from commands.base import CommandBase
from validators import ExitCodePostcondition


class Make(CommandBase):
    def __init__(self, target=None, build_dir='.', **kwargs):
        super().__init__(**kwargs)
        self.build_dir = build_dir
        self.target = target

    def get_command(self):
        target = [] if self.target is None else [self.target]
        return ['make', '-C', self.build_dir] + target

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]


class CMake(CommandBase):
    def __init__(self, source_dir='.', build_dir='build', **kwargs):
        super().__init__(**kwargs)
        self.source_dir = source_dir
        self.build_dir = build_dir

    def get_command(self):
        # TODO: -S replaces -H in newer versions
        return ['cmake', '-B{}'.format(self.build_dir), '-H{}'.format(self.source_dir)]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'CME')
        ]

# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.typing import *
from kolejka.judge.systems.base import SystemBase
from kolejka.judge.commands.base import CommandBase
from kolejka.judge.tasks.base import TaskBase


__all__ = [ 'Checking' ]
def __dir__():
    return __all__


class Checking:
    def __init__(self, system: SystemBase):
        self.steps: Dict[str, CommandBase or TaskBase] = {}
        self.system = system

    def __getattr__(self, key):
        return self.steps[key]

    def __getitem__(self, key):
        return self.steps[key]

    def add_steps(self, *args, **kwargs):
        steps = {}

        existing_indices = [k for k in self.steps.keys() if k.isdecimal()]
        max_index = max(list(map(int, existing_indices)) + [0])
        for i, arg in enumerate(args):
            steps[str(i + max_index + 1)] = arg
        steps.update(kwargs)

        for name, func in steps.items():
            if name in self.steps:
                raise TypeError("Step {} has already been added".format(name))

        for name, func in steps.items():
            self.steps[name] = func

    def run(self):
        return self.system.run_steps(self.steps)

    def format_result(self, result):
        formatted_result = {}
        for key, value in result.items():
            formatted_result[key] = self.system.format_execution_status(value)

        return formatted_result

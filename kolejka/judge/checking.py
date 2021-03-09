# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.systems.base import SystemBase
from kolejka.judge.commands.base import CommandBase
from kolejka.judge.tasks.base import TaskBase


__all__ = [ 'Checking' ]
def __dir__():
    return __all__


class Checking:
    def __init__(self, system, id, test, solution):
        self.steps: Dict[str, CommandBase or TaskBase] = {}
        self.system = system
        self.id = id
        self.test = test
        self.solution = solution
        self.result = None

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
                raise ValueError("Step {} has already been added.".format(name))
            if not isinstance(func, (CommandBase, TaskBase)):
                raise ValueError("Step {} is neither a Command nor a Task.".format(name))

        self.steps.update(steps)

    def run(self):
        self.result = self.system.run_steps(self.steps)
        return self.result

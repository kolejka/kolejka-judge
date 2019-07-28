# vim:ts=4:sts=4:sw=4:expandtab
from copy import deepcopy
import glob
import shlex
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.tasks.build.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import *
from kolejka.judge.commands.compile import *
from kolejka.judge.commands.make import *
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge import config


__all__ = [
        'BuildAutoTask', 'SolutionBuildAutoTask', 'ToolBuildAutoTask',
        ]
def __dir__():
    return __all__


class BuildAutoTask(BuildTask):
    def __init__(self, builders, **kwargs):
        super().__init__(**kwargs)
        self.build_tasks = list()
        for Class, a, k in builders:
            kw = deepcopy(kwargs)
            kw.update(k)
            self.build_tasks += [ Class(*a, **kw) ]
        self.build_task_chosen = False

    def set_system(self, system):
        super().set_system(system)
        for task in self.build_tasks:
            task.set_system(system)

    def set_name(self, name):
        super().set_name(name)
        task_counter = 1
        for task in self.build_tasks:
            task.set_name('%s_%02d'%(name, task_counter))
            task_counter += 1

    def get_build_task(self):
        if not self.build_task_chosen:
            self.build_task = None
            for task in self.build_tasks:
                if task.ok():
                    self.build_task = task
                    break
        return self.build_task

    def ok(self):
        return self.get_build_task() is not None

    def get_execution_command(self):
        task = self.get_build_task()
        if task:
            return task.get_execution_command()

    def execute_build(self):
        task = self.get_build_task()
        if not task:
            return self.result_on_error, self.result
        return task.execute_build()

    def get_result(self):
        task = self.get_build_task()
        if not task:
            return super().get_result()
        return task.get_result()


class SolutionBuildAutoTask(SolutionBuildMixin, BuildAutoTask):
    pass
class ToolBuildAutoTask(ToolBuildMixin, BuildAutoTask):
    pass

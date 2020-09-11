# vim:ts=4:sts=4:sw=4:expandtab


from copy import deepcopy
import glob
import shlex


from kolejka.judge import config
from kolejka.judge.tasks.build.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import TaskBase


__all__ = [
        'BuildAutoTask', 'SolutionBuildAutoTask', 'ToolBuildAutoTask',
        ]
def __dir__():
    return __all__


class BuildAutoTask(BuildTask):
    @default_kwargs
    def __init__(self, builders, **kwargs):
        super().__init__(**kwargs)
        self.build_tasks = list()
        for Class, a, k in builders:
            kw = deepcopy(kwargs)
            kw.update(k)
            self.build_tasks += [ Class(*a, **kw) ]
        self._build_task = None

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

    @property
    def build_task(self):
        return self.get_build_task()
    def get_build_task(self):
        if not self._build_task:
            for task in self.build_tasks:
                if task.ok():
                    self._build_task = task
                    break
        return self._build_task

    def ok(self):
        return self.build_task is not None and self.build_task.ok()

    def get_execution_command(self):
        task = self.build_task
        if task:
            return task.get_execution_command()

    def execute_build(self):
        task = self.build_task
        if not task:
            return self.result_on_error, self.result
        return task.execute_build()

    def get_result(self):
        task = self.build_task
        if not task:
            return super().get_result()
        return task.get_result()

    def set_result(self, *args, **kwargs):
        task = self.build_task
        if not task:
            return super().set_result(*args, **kwargs)
        return task.set_result(*args, **kwargs)


class SolutionBuildAutoTask(SolutionBuildMixin, BuildAutoTask):
    pass
class ToolBuildAutoTask(ToolBuildMixin, BuildAutoTask):
    pass

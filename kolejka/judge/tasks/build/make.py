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
        'BuildCMakeTask', 'SolutionBuildCMakeTask', 'ToolBuildCMakeTask',
        'BuildMakeTask', 'SolutionBuildMakeTask', 'ToolBuildMakeTask',
        ]
def __dir__():
    return __all__


class BuildCMakeTask(BuildTask):
    def ok(self):
        return self.resolve_path(self.source_directory / 'CMakeLists.txt').is_file()

    def execute_build(self):
        status = None
        status = status or self.run_command('cmake', CMakeCommand, source_directory=self.source_directory, build_directory=self.build_directory)
        status = status or self.run_command('make', MakeCommand, build_directory=self.build_directory, build_target=self.build_target)
        return status


class BuildMakeTask(BuildTask):
    def ok(self):
        return self.resolve_path(self.source_directory / 'Makefile').is_file()

    def execute_build(self):
        status = None
        status = status or self.run_command('copy', ProgramCommand, program='rsync', program_arguments=['-a', [self.source_directory,'/'], [self.build_directory,'/']])
        status = status or self.run_command('make', MakeCommand, build_directory=self.build_directory, build_target=self.build_target)
        return status


class SolutionBuildCMakeTask(SolutionBuildMixin, BuildCMakeTask):
    pass
class ToolBuildCMakeTask(ToolBuildMixin, BuildCMakeTask):
    pass

class SolutionBuildMakeTask(SolutionBuildMixin, BuildMakeTask):
    pass
class ToolBuildMakeTask(ToolBuildMixin, BuildMakeTask):
    pass

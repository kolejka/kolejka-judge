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
        'BuildScriptTask', 'SolutionBuildScriptTask', 'ToolBuildScriptTask',
        'BuildBashScriptTask', 'SolutionBuildBashScriptTask', 'ToolBuildBashScriptTask',
        'BuildPython3ScriptTask', 'SolutionBuildPython3ScriptTask', 'ToolBuildPython3ScriptTask',
        ]
def __dir__():
    return __all__


class BuildScriptTask(BuildTask):
    @default_kwargs
    def __init__(self, interpreter=None, source_globs=None, **kwargs):
        super().__init__(**kwargs)
        self.interpreter = interpreter or 'sh'
        self.source_globs = source_globs or ['*']

    def get_source_files(self):
        result = []
        for f in self.find_files(self.source_directory):
            for source_glob in self.source_globs:
                if f.match(source_glob):
                    result += [f]
                    break
        return result

    def ok(self):
        return len(self.get_source_files()) == 1

    def execute_build(self):
        source_file = self.get_source_files()[0]
        target_file = self.build_directory / source_file.name 

        return self.run_command('install', InstallCommand, source=source_file, target=target_file)

    def get_execution_command(self):
        return [ self.interpreter, self.commands['install'].target ]

class SolutionBuildScriptTask(SolutionBuildMixin, BuildScriptTask):
    pass
class ToolBuildScriptTask(ToolBuildMixin, BuildScriptTask):
    pass

class BuildBashScriptTask(BuildScriptTask): 
    DEFAULT_INTERPRETER = 'bash'
    DEFAULT_SOURCE_GLOBS = [
        '*.[Ss][Hh]'
    ]
    @default_kwargs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
class SolutionBuildBashScriptTask(SolutionBuildMixin, BuildBashScriptTask):
    pass
class ToolBuildBashScriptTask(ToolBuildMixin, BuildBashScriptTask):
    pass

class BuildPython3ScriptTask(BuildScriptTask): 
    DEFAULT_INTERPRETER = 'python3'
    DEFAULT_SOURCE_GLOBS = [
        '*.[Pp][Yy]'
    ]
    @default_kwargs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
class SolutionBuildPython3ScriptTask(SolutionBuildMixin, BuildPython3ScriptTask):
    pass
class ToolBuildPython3ScriptTask(ToolBuildMixin, BuildPython3ScriptTask):
    pass

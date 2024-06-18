# vim:ts=4:sts=4:sw=4:expandtab


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
        ]
def __dir__():
    return __all__


class BuildScriptTask(BuildTask):
    @default_kwargs
    def __init__(self, interpreter=None, source_globs=None, main_filename="main", **kwargs):
        super().__init__(**kwargs)
        self.interpreter = interpreter or 'sh'
        self.source_globs = source_globs or ['*']
        self.main_filename = main_filename

    def get_source_files(self, globs=None):
        if globs is None:
            globs = self.source_globs

        result = []
        for f in self.find_files(self.source_directory):
            for source_glob in globs:
                if f.match(source_glob):
                    result += [f]
                    break
        return result

    def ok(self):
        return len(self.get_source_files()) > 0

    def execute_build(self):
        files = self.get_source_files()

        if len(files) == 1:
            source_file = files[0]
        else: 
            basenames = [f.stem for f in files]
            executable = [(file, basename) for file, basename in zip(files, basenames) if basename == self.main_filename]

            if len(executable) != 1:
                return "CME"

            source_file = executable[0][0]

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
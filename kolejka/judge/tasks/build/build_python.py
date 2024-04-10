# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.tasks.build.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge.tasks.build import *

__all__ = [
        'BuildPython3ScriptTask',
        'SolutionBuildPython3ScriptTask',
        'ToolBuildPython3ScriptTask',
]

def __dir__():
    return __all__


class BuildPython3ScriptTask(BuildScriptTask): 
    DEFAULT_INTERPRETER = 'python3'
    DEFAULT_SOURCE_GLOBS = [
        '*.[Pp][Yy]'
    ]
    @default_kwargs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_execution_commands(self):
        base_commands = super().get_execution_commands()
        #if exists:
        env_commands = [".", self.build_directory/"venv/bin/activate"]
        
        result = [env_commands] + base_commands

        return result

    def execute_build(self):
        #self.run_command('install-numpy', InstallPackageIntoVenv, venv="shared/env", package="tqdm")
        
        wheel_globs = ['*.[Ww][Hh][Ll]']
        wheels = self.get_source_files(wheel_globs)

        if wheels:
            self.run_command('venv', CreateVenvCommand, path=self.build_directory/"venv")
        for wheel in wheels:
            semantic_part = str(wheel).split('/')[-1]
            print("Installing wheel", semantic_part)
            result = self.run_command(f'install-{semantic_part}', InstallPackageIntoVenv, venv=self.build_directory/"venv", package=wheel)

            if result is not None:
                return "INT"
            
            self.run_command(f'remove-wheel-file-{semantic_part}', RemoveWheelFile, path=wheel)

        return super().execute_build()

class SolutionBuildPython3ScriptTask(SolutionBuildMixin, BuildPython3ScriptTask):
    pass
    
class ToolBuildPython3ScriptTask(ToolBuildMixin, BuildPython3ScriptTask):
    pass

# vim:ts=4:sts=4:sw=4:expandtab
from copy import deepcopy
import glob
import shlex
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import *
from kolejka.judge.commands.compile import *
from kolejka.judge.commands.make import *
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge import config


__all__ = [
        'BuildTask', 'SolutionBuildTask', 'ToolBuildTask',
        'SolutionBuildMixin', 'ToolBuildMixin',
        ]
def __dir__():
    return __all__


class SolutionBuildMixin:
    DEFAULT_SOURCE_DIRECTORY=config.SOLUTION_SOURCE
    DEFAULT_BUILD_DIRECTORY=config.SOLUTION_BUILD
    DEFAULT_EXECUTION_SCRIPT=config.SOLUTION_EXEC
    DEFAULT_USER=config.USER_BUILD
    DEFAULT_GROUP=config.USER_BUILD
    DEFAULT_RESULT_ON_ERROR='CME'
    @default_kwargs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ToolBuildMixin:
    DEFAULT_SOURCE_DIRECTORY=config.TOOL_SOURCE
    DEFAULT_BUILD_DIRECTORY=config.TOOL_BUILD
    DEFAULT_EXECUTION_SCRIPT=config.TOOL_EXEC
    DEFAULT_USER=config.USER_TEST
    DEFAULT_GROUP=config.USER_TEST
    DEFAULT_RESULT_ON_ERROR='INT'
    @default_kwargs
    def __init__(self, *args, tool_name, **kwargs):
        for arg in [ 'source_directory', 'build_directory', 'execution_script' ]:
            if isinstance(kwargs[arg], str):
                kwargs[arg] = kwargs[arg].format(tool_name=tool_name)
        super().__init__(*args, **kwargs)


class BuildTask(TaskBase):
    def __init__(self, source_directory, build_directory, execution_script=None, build_options=None, build_target=None, **kwargs):
        super().__init__(**kwargs)
        self.source_directory = get_output_path(source_directory)
        self.build_directory = get_output_path(build_directory)
        self.execution_script = get_output_path(execution_script)
        self.build_options = build_options
        self.build_target = build_target and get_relative_path(build_target)

    def write_execution_script(self):
        if self.execution_script:
            execution_command = self.get_execution_command()
            if execution_command:
                execution_script_path = self.resolve_path(self.execution_script)
                execution_script_body = '#!/bin/sh\nexec ' + ' '.join([ shlex.quote(self.system.resolve(a)) for a in execution_command ]) + ' "$@" \n'
                with execution_script_path.open('w') as execution_script_file:
                    execution_script_file.write(execution_script_body)
                execution_script_path.chmod(0o755)

    def find_binary(self, path):
        if self.build_target is not None:
            target_path = self.resolve_path(path / self.build_target)
            if target.is_file() and (target.stat().st_mode & 0o111):
                return path / self.build_target
        binaries = [ f for f in self.find_files(path) if self.resolve_path(f).stat().st_mode & 0o111 ]
        if len(binaries) > 0:
            binary = max(binaries, key=lambda f : self.resolve_path(f).stat().st_mtime, default=None)
            return binary

    def ok(self):
        return False

    def get_execution_command(self):
        return [ self.find_binary(self.build_directory) ]

    def execute(self):
        status = None
        status = status or self.execute_build()
        status = status or self.execute_post_build()
        return status, self.result

    def execute_build(self):
        raise NotImplementedError()

    def execute_post_build(self):
        self.write_execution_script()

class SolutionBuildTask(SolutionBuildMixin, BuildTask):
    pass
class ToolBuildTask(ToolBuildMixin, BuildTask):
    pass

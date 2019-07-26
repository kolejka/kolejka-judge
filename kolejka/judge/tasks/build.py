# vim:ts=4:sts=4:sw=4:expandtab
from copy import deepcopy
import glob
import shlex
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.compile import *
from kolejka.judge.commands.make import *
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge import config


__all__ = [
        'BuildTask', 'SolutionBuildTask', 'ToolBuildTask',
        'BuildAutoTask', 'SolutionBuildAutoTask', 'ToolBuildAutoTask',
        'BuildCMakeTask', 'SolutionBuildCMakeTask', 'ToolBuildCMakeTask',
        'BuildMakeTask', 'SolutionBuildMakeTask', 'ToolBuildMakeTask',
        'BuildGCCTask', 'SolutionBuildGCCTask', 'ToolBuildGCCTask',
        'BuildGXXTask', 'SolutionBuildGXXTask', 'ToolBuildGXXTask',
        ]
def __dir__():
    return __all__


class SolutionMixin:
    DEFAULT_SOURCE_DIRECTORY=config.SOLUTION_SOURCE
    DEFAULT_BUILD_DIRECTORY=config.SOLUTION_BUILD
    DEFAULT_EXECUTION_SCRIPT=config.SOLUTION_EXEC
    DEFAULT_RESULT_ON_ERROR='CME'
    @default_kwargs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ToolMixin:
    DEFAULT_SOURCE_DIRECTORY=config.TOOL_SOURCE
    DEFAULT_BUILD_DIRECTORY=config.TOOL_BUILD
    DEFAULT_EXECUTION_SCRIPT=config.TOOL_EXEC
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
                execution_script_path.chmod(0o550)

    def find_binary(self, path):
        if self.build_target is not None:
            target_path = self.resolve_path(path / self.build_target)
            if target.is_file() and (target.stat().st_mode & 0o111):
                return path / self.build_target
            binaries = [ f for f in self.find_files(path) if self.resolve_path(f).stat().st_mode & 0o111 ]
            if len(binaries) > 0:
                binary = max(binaries, key=lambda f : self.resolve_path(f).stat().st_mtime, default=None)
                return path / binary.relative_to(self.resolve_path(path))

    def ok(self):
        return False

    def get_execution_command(self):
        return self.find_binary(build_path) or self.find_binary(source_path)

    def execute(self):
        status = None
        status = status or self.execute_build()
        status = status or self.execute_post_build()
        return status, self.result

    def execute_build(self):
        raise NotImplementedError()

    def execute_post_build(self):
        self.write_execution_script()


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


class BuildCMakeTask(BuildTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def ok(self):
        return self.resolve_path(self.source_directory / 'CMakeLists.txt').is_file()

    def execute_build(self):
        status = None
        status = status or self.run_command('cmake', CMakeCommand, source_directory=self.source_directory, build_directory=self.build_directory)
        status = status or self.run_command('make', MakeCommand, build_directory=self.build_directory, build_target=self.build_target)
        return status


class BuildMakeTask(BuildTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def ok(self):
        return self.resolve_path(self.source_directory / 'Makefile').is_file()

    def execute_build(self):
        #TODO: How to use build directory?
        status = None
        status = status or self.run_command('make', MakeCommand, build_directory=self.source_directory, build_target=self.build_target)
        return status


class BuildCompilerTask(BuildTask):
    Compiler = None
    source_globs = []
    def __init__(self, libraries=None, **kwargs):
        super().__init__(**kwargs)
        self.libraries = libraries

    def get_source_files(self):
        result = list()
        for f in self.find_files(self.source_directory):
            for source_glob in self.source_globs:
                if f.match(source_glob):
                    result += [f]
                    break
        return result

    def ok(self):
        return len(self.get_source_files()) > 0

    @property
    def compiler_kwargs(self) -> Dict[str, Any]:
        return self.get_compiler_kwargs()
    def get_compiler_kwargs(self):
        kwargs = dict()
        if self.build_directory is not None:
            kwargs['build_directory'] = self.build_directory
        if self.build_options is not None:
            kwargs['build_options'] = self.build_options
        if self.build_target is not None:
            kwargs['build_target'] = self.build_target
        if self.libraries is not None:
            kwargs['libraries'] = self.libraries
        return kwargs

    def execute_build(self):
        status = self.run_command('compile', self.Compiler,
                source_files=self.get_source_files(),
                **self.compiler_kwargs
                )
        return status

    def get_execution_command(self):
        return self.commands['compile'].execution_command

class SolutionBuildTask(SolutionMixin, BuildTask):
    pass
class ToolBuildTask(ToolMixin, BuildTask):
    pass

class SolutionBuildAutoTask(SolutionMixin, BuildAutoTask):
    pass
class ToolBuildAutoTask(ToolMixin, BuildAutoTask):
    pass

class SolutionBuildCMakeTask(SolutionMixin, BuildCMakeTask):
    pass
class ToolBuildCMakeTask(ToolMixin, BuildCMakeTask):
    pass

class SolutionBuildMakeTask(SolutionMixin, BuildMakeTask):
    pass
class ToolBuildMakeTask(ToolMixin, BuildMakeTask):
    pass

class SolutionBuildCompilerTask(SolutionMixin, BuildCompilerTask):
    pass
class ToolBuildCompilerTask(ToolMixin, BuildCompilerTask):
    pass

class BuildGCCTask(BuildCompilerTask):
    Compiler = GCCCommand
    source_globs = [
        '*.[Cc]',
        ]
    def __init__(self, static=None, version=None, standard=None, **kwargs):
        super().__init__(**kwargs)
        self.version = version
        self.standard = standard
        self.static = static
    def get_compiler_kwargs(self):
        kwargs = super().get_compiler_kwargs()
        if self.version is not None:
            kwargs['version'] = self.version
        if self.standard is not None:
            kwargs['standard'] = self.standard
        if self.static is not None:
            kwargs['static'] = self.static
        return kwargs

class SolutionBuildGCCTask(SolutionMixin, BuildGCCTask):
    pass
class ToolBuildGCCTask(ToolMixin, BuildGCCTask):
    pass

class BuildGXXTask(BuildGCCTask):
    Compiler = GXXCommand
    source_globs = [
        '*.[Cc][Pp][Pp]',
        ]
class SolutionBuildGXXTask(SolutionMixin, BuildGXXTask):
    pass
class ToolBuildGXXTask(ToolMixin, BuildGXXTask):
    pass

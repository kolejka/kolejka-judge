# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.tasks.build.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import TaskBase


__all__ = [
        'BuildCompilerTask', 'SolutionBuildCompilerTask', 'ToolBuildCompilerTask',
        'BuildGCCTask', 'SolutionBuildGCCTask', 'ToolBuildGCCTask',
        'BuildGXXTask', 'SolutionBuildGXXTask', 'ToolBuildGXXTask',
        'BuildNVCCTask', 'SolutionBuildNVCCTask', 'ToolBuildNVCCTask', 'SolutionBuildRustTask'
        ]
def __dir__():
    return __all__


class BuildCompilerTask(BuildTask):
    @default_kwargs
    def __init__(self, compiler=None, build_arguments=None, source_globs=None, libraries=None, **kwargs):
        super().__init__(**kwargs)
        self.compiler = compiler or CompileCommand
        self.build_arguments = build_arguments
        self.source_globs = source_globs or []
        self.libraries = libraries

    def get_source_files(self):
        result = []
        for f in self.find_files(self.source_directory):
            for source_glob in self.source_globs:
                if f.match(source_glob):
                    result += [f]
                    break
        return result

    def ok(self):
        return len(self.get_source_files()) > 0

    @property
    def compiler_kwargs(self):
        return self.get_compiler_kwargs()
    def get_compiler_kwargs(self):
        kwargs = dict()
        if self.build_directory is not None:
            kwargs['build_directory'] = self.build_directory
        if self.build_arguments is not None:
            kwargs['build_arguments'] = self.build_arguments
        if self.build_options is not None:
            kwargs['build_options'] = self.build_options
        if self.build_target is not None:
            kwargs['build_target'] = self.build_target
        if self.libraries is not None:
            kwargs['libraries'] = self.libraries
        return kwargs

    def execute_build(self):
        status = self.run_command('compile', self.compiler,
                source_files=self.get_source_files(),
                **self.compiler_kwargs
                )
        return status

    def get_execution_command(self):
        return self.commands['compile'].execution_command


class SolutionBuildCompilerTask(SolutionBuildMixin, BuildCompilerTask):
    pass
class ToolBuildCompilerTask(ToolBuildMixin, BuildCompilerTask):
    pass

class BuildGCCTask(BuildCompilerTask):
    DEFAULT_COMPILER = GCCCommand
    DEFAULT_SOURCE_GLOBS = [
        '*.[Cc]',
        ]
    @default_kwargs
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

class BuildRustTask(BuildCompilerTask):
    DEFAULT_COMPILER = CargoBuildCommand
    DEFAULT_SOURCE_GLOBS = [
        '*.[Rr][Ss]',
    ]
    
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute_build(self):     
        env = self.get_rust_envs()
        
        cargo_project_path = self.build_directory/config.CARGO_PROJECT_NAME
        project_config_path = cargo_project_path/config.CARGO_CONFIG_FILE

        self.run_command(
            "move_libraries",
            MoveCommand,
            environment=env,
            source=self.source_directory/config.CARGO_DEPENDENCIES_DIR,
            target=self.build_directory/config.CARGO_DEPENDENCIES_DIR)
        
        self.run_command(
            "cargo_new",
            CargoNewCommand,
            environment=env,
            path=cargo_project_path
        )
        
        self.run_command(
            "copy_source",
            CopySourceCommand,
            environment=env,
            source=self.source_directory,
            target=cargo_project_path/config.CARGO_SOURCE_DIR
        )
        
        dependency_directories = self.find_directories(self.build_directory/config.CARGO_DEPENDENCIES_DIR)
        
        for dep_dir in dependency_directories:
            effective_name = str(dep_dir).split("/")[-1]
            self.run_command(
                f"install_{effective_name}",
                AddOfflineDependency,
                environment=env,
                project_path=project_config_path,
                dep_path=dep_dir
            )

        return super().execute_build() 
    
    def get_compiler_kwargs(self):
        kwargs = super().get_compiler_kwargs()
                
        kwargs["cargo_config_file"] = self.build_directory/config.CARGO_PROJECT_NAME/config.CARGO_CONFIG_FILE
        kwargs['build_target'] = get_relative_path(config.CARGO_PROJECT_NAME)/config.CARGO_BUILD_DIR

        kwargs['environment'] = self.get_rust_envs()

        return kwargs
    
    def get_rust_envs(self):
        if config.RUSTUP_HOME and config.CARGO_HOME:
            return {
                'RUSTUP_HOME': config.RUSTUP_HOME,
                'CARGO_HOME': config.CARGO_HOME
            }
        else: 
            return {}
    
class SolutionBuildGCCTask(SolutionBuildMixin, BuildGCCTask):
    pass
class ToolBuildGCCTask(ToolBuildMixin, BuildGCCTask):
    pass

class BuildGXXTask(BuildGCCTask):
    DEFAULT_COMPILER = GXXCommand
    DEFAULT_SOURCE_GLOBS = [
        '*.[Cc][Pp][Pp]',
        '*.[Cc][Cc]',
        ]
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
class SolutionBuildGXXTask(SolutionBuildMixin, BuildGXXTask):
    pass
class SolutionBuildRustTask(SolutionBuildMixin, BuildRustTask):
    pass 
class ToolBuildGXXTask(ToolBuildMixin, BuildGXXTask):
    pass

class BuildNVCCTask(BuildGCCTask):
    DEFAULT_COMPILER = NVCCCommand
    DEFAULT_SOURCE_GLOBS = [
        '*.[Cc][Uu]',
        ]
    @default_kwargs
    def __init__(self, architecture=None, **kwargs):
        super().__init__(**kwargs)
        self.architecture = architecture
    def get_compiler_kwargs(self):
        kwargs = super().get_compiler_kwargs()
        if self.architecture is not None:
            kwargs['architecture'] = self.architecture
        return kwargs

class SolutionBuildNVCCTask(SolutionBuildMixin, BuildNVCCTask):
    pass
class ToolBuildNVCCTask(ToolBuildMixin, BuildNVCCTask):
    pass

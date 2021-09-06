# vim:ts=4:sts=4:sw=4:expandtab
from copy import deepcopy


from kolejka.judge import config
from kolejka.judge.commands import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.tasks.base import TaskBase
from kolejka.judge.tasks.build import *
from kolejka.judge.tasks.prepare import *
from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.system import *
from kolejka.judge.systems.base import SystemBase


__all__ = [ 'ToolTask', 'GeneratorTask', 'VerifierTask', 'HinterTask', 'CheckerTask' ]
def __dir__():
    return __all__


class ToolTask(TaskBase):
    DEFAULT_RESULT_ON_ERROR='INT'
    DEFAULT_USER_NAME=config.USER_TEST
    DEFAULT_GROUP_NAME=config.USER_TEST
    DEFAULT_CPP_STANDARD=config.TOOL_BUILD_CPP_STANDARD
    DEFAULT_CUDA_ARCHITECTURE=config.TOOL_BUILD_CUDA_ARCHITECTURE
    DEFAULT_PREPARE_TASK=None
    DEFAULT_BUILD_TASK=None
    DEFAULT_EXECUTE_TASK=None
    @default_kwargs
    def __init__(self, tool_name,
            user_name, group_name,
            source=None, override=None, source_directory=None, build_directory=None,
            arguments=None, input_path=None, output_path=None, error_path=None,
            cpp_standard=None,
            cuda_architecture=None,
            libraries=None,
            prepare_task=None,
            build_task=None,
            execute_task=None,
            **kwargs):

        super().__init__(**kwargs)
        self._tool_name = tool_name
        self._user_name = user_name
        self._group_name = group_name
        self._source = source
        self._override = override
        self._source_directory = source_directory
        self._build_directory = build_directory
        self._prepare_kwargs = kwargs
        self._build_kwargs = kwargs
        self._execute_kwargs = kwargs
        self._prepare_task = prepare_task
        self._build_task = build_task
        self._execute_task = execute_task
        self.arguments = arguments
        self.input_path = input_path
        self.output_path = output_path
        self.error_path = error_path
        self.cpp_standard = cpp_standard
        self.cuda_architecture = cuda_architecture
        self.libraries = libraries

        self.prepare_task = self.prepare_task_factory()
        self.build_task = self.build_task_factory()
        self.execute_task = self.execute_task_factory()

        self.input_path = self.execute_task.stdin
        self.output_path = self.execute_task.stdout
        self.error_path = self.execute_task.stderr

    def prepare_task_factory(self):
        if self._prepare_task is None:
            return ToolPrepareTask(**self.prepare_kwargs)
        else:
            return self._prepare_task(**self.prepare_kwargs)
        
    def build_task_factory(self):
        if self._build_task is None:
            sub_kwargs = { 'tool_name' : self.tool_name }
            gxx_kwargs = deepcopy(sub_kwargs)
            gcc_kwargs = deepcopy(sub_kwargs)
            nvcc_kwargs = deepcopy(sub_kwargs)
            nvcc_kwargs['architecture'] = self.cuda_architecture
            nvcc_kwargs['standard'] = self.cpp_standard
            nvcc_kwargs['libraries'] = self.libraries
            gxx_kwargs['standard'] = self.cpp_standard
            gxx_kwargs['libraries'] = self.libraries
            gcc_kwargs['libraries'] = self.libraries
            return ToolBuildAutoTask([
            [ToolBuildCMakeTask, [], sub_kwargs],
            [ToolBuildMakeTask, [], sub_kwargs],
            [ToolBuildNVCCTask, [], nvcc_kwargs],
            [ToolBuildGXXTask, [], gxx_kwargs],
            [ToolBuildGCCTask, [], gcc_kwargs],
            [ToolBuildPython3ScriptTask, [], sub_kwargs],
            [ToolBuildBashScriptTask, [], sub_kwargs],
            ], **self.build_kwargs)
        else:
            return self._build_task(**self.build_kwargs)

    def execute_task_factory(self):
        if self._execute_task is None:
            return ToolExecutableTask(**self.execute_kwargs)
        else:
            return self._execute_task(**self.execute_kwargs)
    
    @property
    def tool_name(self):
        return self.get_tool_name()
    def get_tool_name(self):
        return self._tool_name
    @property
    def user_name(self):
        return self.get_user_name()
    def get_user_name(self):
        return self._user_name
    @property
    def group_name(self):
        return self.get_group_name()
    def get_group_name(self):
        return self._group_name
    @property
    def source(self):
        return self.get_source()
    def get_source(self):
        return self._source
    @property
    def override(self):
        return self.get_override()
    def get_override(self):
        return self._override
    @property
    def source_directory(self):
        return self.get_source_directory()
    def get_source_directory(self):
        return self._source_directory
    @property
    def build_directory(self):
        return self.get_build_directory()
    def get_build_directory(self):
        return self._build_directory
    @property
    def prepare_kwargs(self):
        return self.get_prepare_kwargs()
    def get_prepare_kwargs(self):
        prepare_kwargs = deepcopy(self._prepare_kwargs)
        prepare_kwargs['result_on_error'] = 'INT'
        prepare_kwargs['tool_name'] = self.tool_name
        prepare_kwargs['user_name'] = self.user_name
        prepare_kwargs['group_name'] = self.group_name
        if self.source:
            prepare_kwargs['source'] = self.source
        if self.override:
            prepare_kwargs['override'] = self.override
        if self.source_directory:
            prepare_kwargs['target'] = self.source_directory
        return prepare_kwargs
    @property
    def build_kwargs(self):
        return self.get_build_kwargs()
    def get_build_kwargs(self):
        build_kwargs = deepcopy(self._build_kwargs)
        build_kwargs['result_on_error'] = 'INT'
        build_kwargs['tool_name'] = self.tool_name
        build_kwargs['source_directory'] = self.prepare_task.target
        if self.build_directory:
            build_kwargs['build_directory'] = self.build_directory
        return build_kwargs
    @property
    def execute_kwargs(self):
        return self.get_execute_kwargs()
    def get_execute_kwargs(self):
        kwargs = deepcopy(self._execute_kwargs)
        kwargs['result_on_error'] = self.result_on_error
        kwargs['tool_name'] = self.tool_name
        if self.input_path:
            kwargs['stdin'] = self.input_path
        if self.output_path:
            kwargs['stdout'] = self.output_path
        if self.error_path:
            kwargs['stderr'] = self.error_path
        kwargs['executable'] = self.build_task.execution_script
        kwargs['executable_arguments'] = self.arguments
        return kwargs

    def set_system(self, system):
        super().set_system(system)
        self.prepare_task.set_system(system)
        self.build_task.set_system(system)
        self.execute_task.set_system(system)

    def set_name(self, name):
        super().set_name(name)
        self.prepare_task.set_name(name+'_prepare')
        self.build_task.set_name(name+'_build')
        self.execute_task.set_name(name+'_exec')

    def execute(self):
        status = None
        tool_exists = len(list(self.find_files(self.build_task.execution_script))) > 0
        if not tool_exists:
            self.run_command('dir_source', DirectoryAddCommand, path=self.prepare_task.target, user_name=self.user_name, group_name=self.group_name, mode=0o2750)
            self.run_command('dir_build', DirectoryAddCommand, path=self.build_task.build_directory, user_name=self.user_name, group_name=self.group_name, mode=0o2750)
            if not status:
                result = self.prepare_task.execute()
                status = result and result.status
                self.set_result(status, 'prepare', result)
            if not status:
                result = self.build_task.execute()
                status = result and result.status
                self.set_result(status, 'build', result)
        if not status:
            result = self.execute_task.execute()
            status = result and result.status
            self.set_result(status, 'exec', result)
        return self.result


class GeneratorTask(ToolTask):
    DEFAULT_TOOL_NAME='generator'
    DEFAULT_OUTPUT_PATH=config.TEST_INPUT
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class VerifierTask(ToolTask):
    DEFAULT_TOOL_NAME='verifier'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class HinterTask(ToolTask):
    DEFAULT_TOOL_NAME='hinter'
    DEFAULT_OUTPUT_PATH=config.TEST_HINT
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CheckerTask(ToolTask):
    DEFAULT_TOOL_NAME='checker'
    DEFAULT_RESULT_ON_ERROR='ANS'
    DEFAULT_ANSWER_PATH=config.TEST_ANSWER
    @default_kwargs
    def __init__(self, input_path, hint_path, answer_path, **kwargs):
        self.input_path = input_path and get_output_path(input_path)
        self.hint_path = hint_path and get_output_path(hint_path)
        self.answer_path = answer_path and get_output_path(answer_path)
        super().__init__(arguments=[self.input_path, self.hint_path, self.answer_path], **kwargs)


    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.input_path),
            FileExistsPrerequirement(self.hint_path),
            FileExistsPrerequirement(self.answer_path),
        ]

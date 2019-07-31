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
    @default_kwargs
    def __init__(self, tool_name,
            user_name, group_name,
            source=None, override=None, source_directory=None, build_directory=None,
            arguments=None, input_path=None, output_path=None, error_path=None,
            **kwargs):

        super().__init__(**kwargs)
        self._tool_name = tool_name
        self._user_name = user_name
        self._group_name = group_name

        source_kwargs = deepcopy(kwargs)
        source_kwargs['result_on_error'] = 'INT'
        source_kwargs['tool_name'] = self.tool_name
        source_kwargs['user_name'] = user_name
        source_kwargs['group_name'] = group_name
        if source:
            source_kwargs['source'] = source
        if override:
            source_kwargs['override'] = override
        if source_directory:
            source_kwargs['target'] = source_directory
        self.source = ToolPrepareTask(**source_kwargs)
        
        sub_kwargs = { 'tool_name' : self.tool_name }
        build_kwargs = deepcopy(kwargs)
        build_kwargs['result_on_error'] = 'INT'
        build_kwargs['tool_name'] = self.tool_name
        build_kwargs['source_directory'] = self.source.target
        if build_directory:
            build_kwargs['build_directory'] = build_directory
        self.build = ToolBuildAutoTask([
            [ToolBuildCMakeTask, [], sub_kwargs],
            [ToolBuildMakeTask, [], sub_kwargs],
            [ToolBuildGXXTask, [], sub_kwargs],
            ], **build_kwargs)
        
        executable_kwargs = deepcopy(kwargs)
        executable_kwargs['result_on_error'] = self.result_on_error
        executable_kwargs['tool_name'] = self.tool_name
        if input_path:
            executable_kwargs['stdin'] = input_path
        if output_path:
            executable_kwargs['stdout'] = output_path
        if error_path:
            executable_kwargs['stderr'] = error_path
        executable_kwargs['executable'] = self.build.execution_script
        executable_kwargs['executable_arguments'] = arguments
        self.executable = ToolExecutableTask(**executable_kwargs)
        self.input_path = self.executable.stdin
        self.output_path = self.executable.stdout
        self.error_path = self.executable.stderr

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

    def set_system(self, system):
        super().set_system(system)
        self.source.set_system(system)
        self.build.set_system(system)
        self.executable.set_system(system)

    def set_name(self, name):
        super().set_name(name)
        self.source.set_name(name+'_source')
        self.build.set_name(name+'_build')
        self.executable.set_name(name+'_exec')

    def execute(self):
        self.run_command('dir_source', DirectoryAddCommand, path=self.source.target, user_name=self.user_name, group_name=self.group_name, mode=0o2750)
        self.run_command('dir_build', DirectoryAddCommand, path=self.build.build_directory, user_name=self.user_name, group_name=self.group_name, mode=0o2750)
        status = None
        if not status:
            result = self.source.execute()
            status = result and result.status
            self.set_result(status, 'source', result)
        if not status:
            result = self.build.execute()
            status = result and result.status
            self.set_result(status, 'build', result)
        if not status:
            result = self.executable.execute()
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

# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import *


__all__ = [ 'PrepareTask', 'SolutionPrepareTask', 'ToolPrepareTask' ]
def __dir__():
    return __all__


class PrepareTask(TaskBase):
    DEFAULT_RECORD_RESULT=False
    @default_kwargs
    def __init__(self, source, target, allow_extract=False, user_name=None, group_name=None, override=None, **kwargs):
        super().__init__(**kwargs)
        self.source = get_output_path(source)
        self.target = get_output_path(target)
        self.allow_extract = bool(allow_extract)
        self.user_name = str(user_name)
        self.group_name = str(group_name)
        self.override = override and get_output_path(override)

    def prepare_source(self, name, source):
        sufs = [ s.lower()[1:] for s in source.suffixes ]
        cmd_name = '%s_extract'%(name,)
        if self.allow_extract and sufs[-1] == 'zip':
            return self.run_command(cmd_name, UnzipCommand, source=source, target=self.target)
        if self.allow_extract and sufs[-1] == 'rar':
            return self.run_command(cmd_name, UnrarCommand, source=source, target=self.target)
        if self.allow_extract and sufs[-1] == '7z':
            return self.run_command(cmd_name, Un7zCommand, source=source, target=self.target)
        if self.allow_extract and 'tar' in sufs:
            return self.run_command(cmd_name, UntarCommand, source=source, target=self.target)
        cmd_name = '%s_install'%(name,)
        return self.run_command(cmd_name, InstallCommand, source=source, target=self.target / source.name)

    def execute(self):
        status = self.prepare_source('source', self.source)
        if self.override:
            status = status or self.prepare_source('override', self.override)
        if self.user_name or self.group_name:
            status = status or self.run_command('chown', ChownDirCommand, target=self.target, recursive=True, user_name=self.user_name, group_name=self.group_name)
            status = status or self.run_command('chmod_d', ProgramCommand, program='find', program_arguments=[self.target, '-type', 'd', '-exec', 'chmod', 'o-rwx,g-w+rx,u+rwx', '{}', '+'])
            status = status or self.run_command('chmod_f', ProgramCommand, program='find', program_arguments=[self.target, '-type', 'f', '-exec', 'chmod', 'o-rwx,g-w+r,u+rw', '{}', '+'])
#            status = status or self.run_command('chmod', ProgramCommand, program='chmod', program_arguments=['o-rwx,g-w+rx,u+rwx', '-R', self.target], safe=True)
        print(status)
        self.set_result(status)
        return self.result


class SolutionPrepareTask(PrepareTask):
    DEFAULT_TARGET=config.SOLUTION_SOURCE
    DEFAULT_USER_NAME=config.USER_TEST
    DEFAULT_GROUP_NAME=config.USER_BUILD
    DEFAULT_RESULT_ON_ERROR='CME'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ToolPrepareTask(PrepareTask):
    DEFAULT_TARGET=config.TOOL_SOURCE
    DEFAULT_USER_NAME=config.USER_TEST
    DEFAULT_GROUP_NAME=config.USER_TEST
    DEFAULT_RESULT_ON_ERROR='INT'
    DEFAULT_ALLOW_EXTRACT=True
    @default_kwargs
    def __init__(self, tool_name, **kwargs):
        for arg in [ 'target' ]:
            if isinstance(kwargs[arg], str):
                kwargs[arg] = kwargs[arg].format(tool_name=tool_name)
        super().__init__(**kwargs)

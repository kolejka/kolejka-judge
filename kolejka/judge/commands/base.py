# vim:ts=4:sts=4:sw=4:expandtab


from copy import deepcopy
import pathlib
import pwd


from kolejka.judge import config
from kolejka.judge.exceptions import PrerequirementException
from kolejka.judge.limits import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'CommandBase', 'ExecutableCommand', 'ProgramCommand', ]
def __dir__():
    return __all__


class CommandDefaultOutput:
    def __bool__(self):
        return False
    def __repr__(self):
        return 'DEFAULT'
DEFAULT_OUTPUT = CommandDefaultOutput()


class CommandBase(AbstractCommand):
    def __init__(self, name=None, system=None, work_directory=None, environment=None, user=None, group=None, limits=None, stdin=None, stdout=DEFAULT_OUTPUT, stdout_append=False, stdout_max_bytes=None, stderr=DEFAULT_OUTPUT, stderr_append=False, stderr_max_bytes=None, verbose=False, default_logs=True, obligatory=False, safe=False, background=False,):
        self._name = name
        self._system = system
        self._work_directory = work_directory or get_output_path('.')
        self._environment = dict(environment or {})
        self._user = user and str(user)
        self._group = group and str(group)
        self._limits = limits or get_limits()
        self._stdin = stdin and get_output_path(stdin)
        self._stdout = stdout and get_output_path(stdout)
        self._stdout_append = bool(stdout_append)
        self._stdout_max_bytes = int(stdout_max_bytes) if stdout_max_bytes is not None else None
        self._stderr = stderr and get_output_path(stderr)
        self._stderr_append = bool(stderr_append)
        self._stderr_max_bytes = int(stderr_max_bytes) if stderr_max_bytes is not None else None
        self._verbose = bool(verbose)
        self._default_logs = bool(default_logs)
        self._obligatory = bool(obligatory)
        self._safe = bool(safe)
        self._background = bool(background)
        self._result = None
        self._sequence_id = None
        self._prerequirements = list()
        self._postconditions = list()

    def __repr__(self):
        repr_dict = dict()
        for k,v in self.__dict__.items():
            if k in [ '_system', '_name' ]:
                continue
            if len(k) and k[0] == '_':
                k=k[1:]
            repr_dict[k] = repr(v)
        rep = f'{self.__class__.__name__} ({self.name}): {repr_dict}'
        return rep

    @property
    def name(self):
        name = self.get_name()
        if not name:
            raise RuntimeError('Name not available yet')
        return name
    def get_name(self):
        return self._name
    def set_name(self, name):
        self._name = name

    @property
    def system(self):
        system = self.get_system()
        if not system:
            raise RuntimeError('System not available yet')
        return system
    def get_system(self):
        return self._system
    def set_system(self, system):
        self._system = system

    @property
    def work_directory(self):
        return self.get_work_directory()
    def get_work_directory(self):
        return self._work_directory

    @property
    def environment(self):
        return self.get_environment()
    def get_environment(self):
        environment = deepcopy(self._environment)
        environment['PWD'] = self.work_directory
        environment['SHELL'] = '/bin/bash'
        if self.user:
            environment['USER'] = self.user
            environment['USERNAME'] = self.user
            environment['LOGNAME'] = self.user
            home = self.system.get_home(self.user)
            if home:
                environment['HOME'] = home 
                environment['XDG_RUNTIME_DIR'] = home
        return environment

    @property
    def user(self):
        return self.get_user()
    def get_user(self):
        return self._user

    @property
    def group(self):
        return self.get_group()
    def get_group(self):
        return self._group

    @property
    def limits(self):
        return self.get_limits()
    def get_limits(self):
        return self._limits

    @property
    def stdin(self):
        return self.get_stdin()
    def get_stdin(self):
        return self._stdin

    @property
    def stdout(self):
        return self.get_stdout()
    def get_stdout(self):
        return self._stdout

    @property
    def stdout_append(self):
        return self.get_stdout_append()
    def get_stdout_append(self):
        return self._stdout_append
    
    @property
    def stdout_max_bytes(self):
        return self.get_stdout_max_bytes()
    def get_stdout_max_bytes(self):
        return self._stdout_max_bytes

    @property
    def stderr(self):
        return self.get_stderr()
    def get_stderr(self):
        return self._stderr

    @property
    def stderr_append(self):
        return self.get_stderr_append()
    def get_stderr_append(self):
        return self._stderr_append

    @property
    def stderr_max_bytes(self):
        return self.get_stderr_max_bytes()
    def get_stderr_max_bytes(self):
        return self._stderr_max_bytes

    @property
    def verbose(self):
        return self.get_verbose()
    def get_verbose(self):
        return self._verbose

    @property
    def default_logs(self):
        return self.get_default_logs()
    def get_default_logs(self):
        return self._default_logs

    @property
    def obligatory(self):
        return self.get_obligatory()
    def get_obligatory(self):
        return self._obligatory

    @property
    def safe(self):
        return self.get_safe()
    def get_safe(self):
        return self._safe

    @property
    def background(self):
        return self.get_background()
    def get_background(self):
        return self._background

    @property
    def result(self):
        return self.get_result()
    def get_result(self):
        return self._result
    def set_result(self, result):
        self._result = result

    @property
    def command(self):
        return self.get_command()
    def get_command(self):
        raise NotImplementedError

    _sequence_id_generator = 0
    @property
    def sequence_id(self):
        if self._sequence_id is None:
            CommandBase._sequence_id_generator += 1
            self._sequence_id = CommandBase._sequence_id_generator
        return self._sequence_id

    def get_log_path(self, suffix):
        if self.default_logs:
            file_name = '%03d_%s_%s.txt'%(self.sequence_id, self.name, suffix)
            return self.system.log_directory / file_name
    
    @property
    def work_path(self):
        return self.resolve_path(self.work_directory)
    @property
    def stdin_path(self):
        return self.resolve_path(self.stdin)
    @property
    def stdout_path(self):
        stdout = self.stdout
        if isinstance(stdout, CommandDefaultOutput):
            stdout = self.get_log_path('stdout')
        return self.resolve_path(stdout)
    @property
    def stderr_path(self):
        stderr = self.stderr
        if isinstance(stderr, CommandDefaultOutput):
            stderr = self.get_log_path('stderr')
        return self.resolve_path(stderr)

    @property
    def prerequirements(self):
        return self.get_prerequirements()
    def get_prerequirements(self):
        requirements = [
            DirectoryExistsPrerequirement(self.work_directory),
            SystemUserExistsPrerequirement(self.user),
            SystemGroupExistsPrerequirement(self.group),
            FileExistsPrerequirement(self.stdin),
        ]
        requirements += self._prerequirements
        return requirements
    def add_prerequirement(self, requirement):
        self._prerequirements.append(requirement)

    @property
    def postconditions(self):
        return self.get_postconditions()
    def get_postconditions(self):
        conditions = []
        conditions += self._postconditions
        return conditions
    def add_postcondition(self, condition, status):
        self._postconditions.append((condition, status))

    def verify_prerequirements(self):
        for requirement in self.prerequirements:
            if not requirement(self.system):
                raise PrerequirementException("Prerequirement `{}` not satisfied for {}".format(requirement, self.name))

    def verify_postconditions(self):
        for condition, status in self.postconditions:
            if not condition(self.system, self.result):
                return status

    def resolve_path(self, path):
        return self.system.resolve_path(path, work_directory=self.work_directory)

    def resolve(self, obj):
        return self.system.resolve(obj, work_directory=self.work_directory)

    def find_files(self, path):
        return self.system.find_files(path, work_directory=self.work_directory)

    @property
    def resolved_command(self):
        command = self.command
        if not command:
            return command
        return [ self.resolve(part) for part in command ]
    
    def update_environment(self, environment =dict()):
        env = dict()
        for key, value in environment.items():
            env[key] = self.resolve(value)
        for key, value in self.environment.items():
            if value is None and key in env:
                del env[key]
            else:
                env[key] = self.resolve(value)
        return env


class ExecutableCommand(CommandBase):
    @default_kwargs
    def __init__(self, executable, executable_arguments=None, verbose_arguments=None, quiet_arguments=None, **kwargs):
        super().__init__(**kwargs)
        self._executable = get_output_path(executable)
        self._executable_arguments = executable_arguments or []
        self._verbose_arguments = verbose_arguments or []
        self._quiet_arguments = quiet_arguments or []

    @property
    def executable(self):
        return self.get_executable()
    def get_executable(self):
        return self._executable

    @property
    def executable_arguments(self):
        return self.get_executable_arguments()
    def get_executable_arguments(self):
        return self._executable_arguments

    @property
    def verbose_arguments(self):
        return self.get_verbose_arguments()
    def get_verbose_arguments(self):
        return self._verbose_arguments

    @property
    def quiet_arguments(self):
        return self.get_quiet_arguments()
    def get_quiet_arguments(self):
        return self._quiet_arguments

    def get_command(self):
        command = [ self.executable, ]
        if self.verbose:
            command += self.verbose_arguments
        else:
            command += self.quiet_arguments
        command += self.executable_arguments
        return command

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            ProgramExistsPrerequirement(self.executable),
        ]


class ProgramCommand(CommandBase):
    @default_kwargs
    def __init__(self, program, program_arguments=None, verbose_arguments=None, quiet_arguments=None, **kwargs):
        super().__init__(**kwargs)
        self._program = str(pathlib.Path(program))
        self._program_arguments = program_arguments or []
        self._verbose_arguments = verbose_arguments or []
        self._quiet_arguments = quiet_arguments or []

    @property
    def program(self):
        return self.get_program()
    def get_program(self):
        return self._program

    @property
    def program_arguments(self):
        return self.get_program_arguments()
    def get_program_arguments(self):
        return self._program_arguments

    @property
    def verbose_arguments(self):
        return self.get_verbose_arguments()
    def get_verbose_arguments(self):
        return self._verbose_arguments

    @property
    def quiet_arguments(self):
        return self.get_quiet_arguments()
    def get_quiet_arguments(self):
        return self._quiet_arguments

    def get_command(self):
        command = [ self.program, ]
        if self.verbose:
            command += self.verbose_arguments
        else:
            command += self.quiet_arguments
        command += self.program_arguments
        return command

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement(self.program),
        ]

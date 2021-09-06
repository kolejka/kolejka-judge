# vim:ts=4:sts=4:sw=4:expandtab
import pathlib


from kolejka.judge import config
from kolejka.judge.exceptions import PrerequirementException
from kolejka.judge.limits import *
from kolejka.judge.paths import *
from kolejka.judge.result import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'TaskBase' ]
def __dir__():
    return __all__


class TaskBase(AbstractTask):
    def __init__(self, name=None, system=None, work_directory=None, environment=None, user=None, group=None, limits=None, limit_cpu_time=None, limit_real_time=None, limit_memory=None, limit_gpu_time=None, limit_gpu_memory=None, limit_cores=None, limit_pids=None, verbose=None, default_logs=None, result_on_error=None, result_on_time=None, result_on_memory=None, record_result=True, obligatory=False, safe=None, **kwargs):
        self._name = name
        self._system = system
        self._work_directory = work_directory and get_output_path(work_directory)
        self._environment = environment
        self._user = user
        self._group = group
        self._limits = limits and get_limits(limits)
        if limit_cpu_time:
            self._limits = self._limits or get_limits()
            self._limits.update_cpu_time(limit_cpu_time)
        if limit_real_time:
            self._limits = self._limits or get_limits()
            self._limits.update_real_time(limit_real_time)
        if limit_memory:
            self._limits = self._limits or get_limits()
            self._limits.update_memory(limit_memory)
        if limit_gpu_time:
            self._limits = self._limits or get_limits()
            self._limits.update_gpu_time(limit_gpu_time)
        if limit_gpu_memory:
            self._limits = self._limits or get_limits()
            self._limits.update_gpu_memory(limit_gpu_memory)
        if limit_cores:
            self._limits = self._limits or get_limits()
            self._limits.update_cores(limit_cores)
        if limit_pids:
            self._limits = self._limits or get_limits()
            self._limits.update_pids(limit_pids)
        self._verbose = verbose
        self._default_logs = default_logs
        self._result_on_error = result_on_error
        self._result_on_time = result_on_time
        self._result_on_memory = result_on_memory
        self._record_result = bool(record_result)
        self._obligatory = bool(obligatory)
        self._safe = safe
        self._commands = dict()
        self._result = ResultDict()
        self._prerequirements = list()

    def __repr__(self):
        repr_dict = dict()
        for k,v in self.__dict__.items():
            if k in [ '_system', '_name' ]:
                continue
            if len(k) and k[0] == '_':
                k=k[1:]
            repr_dict[k] = repr(v)
        rep = '%s (%s) : %s'%(self.__class__.__name__, self.name, repr(repr_dict))
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
        return self._environment

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
    def result_on_error(self):
        return self.get_result_on_error()
    def get_result_on_error(self):
        return self._result_on_error

    @property
    def result_on_time(self):
        return self.get_result_on_time()
    def get_result_on_time(self):
        return self._result_on_time

    @property
    def result_on_memory(self):
        return self.get_result_on_memory()
    def get_result_on_memory(self):
        return self._result_on_memory

    @property
    def record_result(self):
        return self.get_record_result()
    def get_record_result(self):
        return self._record_result

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
    def result(self):
        return self.get_result()
    def get_result(self):
        return self._result
    def set_result(self, status =None, name =None, value =None):
        if status is not None:
            self._result.set_status(status)
        if name is not None:
            self._result.set(name, value)
    @property
    def status(self):
        return self.result.status

    @property
    def commands(self):
        return self.get_commands()
    def get_commands(self):
        return self._commands
    def set_command(self, name, value):
        self._commands[name] = value

    @property
    def command_kwargs(self):
        return self.get_command_kwargs()
    def get_command_kwargs(self):
        kwargs = dict()
        work_directory = self.work_directory
        if work_directory is not None:
            kwargs['work_directory'] = work_directory
        environment = self.environment
        if environment is not None:
            kwargs['environment'] = environment
        user = self.user
        if user is not None:
            kwargs['user'] = user
        group = self.group
        if group is not None:
            kwargs['group'] = group
        limits = self.limits
        if limits is not None:
            kwargs['limits'] = limits
        verbose = self.verbose
        if verbose is not None:
            kwargs['verbose'] = verbose
        default_logs = self.default_logs
        if default_logs is not None:
            kwargs['default_logs'] = default_logs
        safe = self.safe
        if safe is not None:
            kwargs['safe'] = safe
        return kwargs

    @property
    def command_prerequirements(self):
        return self.get_command_prerequirements()
    def get_command_prerequirements(self):
        requirements = []
        return requirements
    
    @property
    def command_postconditions(self):
        return self.get_command_postconditions()
    def get_command_postconditions(self):
        conditions = []
        if self.result_on_time is not None:
            cpu_time = self.limits and self.limits.cpu_time
            real_time = self.limits and self.limits.real_time
            gpu_time = self.limits and self.limits.gpu_time
            conditions += [
                (TimeLimitPostcondition(cpu_time=cpu_time, real_time=real_time, gpu_time=gpu_time), self.result_on_time)
            ]
        if self.result_on_memory is not None:
            memory = self.limits and self.limits.memory
            gpu_memory = self.limits and self.limits.gpu_memory
            conditions += [
                (MemoryLimitPostcondition(memory=memory, gpu_memory=gpu_memory), self.result_on_memory)
            ]
        if self.result_on_error is not None:
            conditions += [
                (ReturnCodePostcondition(), self.result_on_error)
            ]
        return conditions

    def run_command(self, name, Command, system=None, **kwargs):
        cmd_name = '%s_%s'%(self.name, name)
        system = self.system
        command_kwargs = self.command_kwargs
        command_kwargs.update(kwargs)
        cmd = Command(name=cmd_name, system=system, **command_kwargs)
        for requirement in self.command_prerequirements:
            cmd.add_prerequirement(requirement)
        for condition in self.command_postconditions:
            cmd.add_postcondition(*condition)
        result = self.system.run_command(cmd, name=cmd_name)
        self.set_result(None, name, result)
        self.set_command(name, cmd)
        return result and result.status

    def execute(self):
        raise NotImplementedError

    @property
    def prerequirements(self):
        return self.get_prerequirements()
    def get_prerequirements(self):
        requirements = [
            DirectoryExistsPrerequirement(self.work_directory),
            SystemUserExistsPrerequirement(self.user),
            SystemGroupExistsPrerequirement(self.group),
        ]
        requirements += self._prerequirements
        return requirements
    def add_prerequirement(self, requirement):
        self._prerequirements.append(requirement)

    def verify_prerequirements(self):
        for requirement in self.prerequirements:
            if not requirement(self.system):
                raise PrerequirementException("Prerequirement `{}` not satisfied for {}".format(requirement, self.name))

    def resolve_path(self, path):
        return self.system.resolve_path(path, work_directory=self.work_directory)

    def find_files(self, path):
        return self.system.find_files(path, work_directory=self.work_directory)

    def file_contents(self, path):
        return self.system.file_contents(path, work_directory=self.work_directory)

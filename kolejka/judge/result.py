# vim:ts=4:sts=4:sw=4:expandtab


from collections import OrderedDict
import datetime
import pathlib


from kolejka.judge import config
from kolejka.judge.limits import get_limits
from kolejka.judge.parse import parse_memory, parse_time, unparse_memory, unparse_time
from kolejka.judge.typing import *


__all__ = [ 'Result', 'ResultDict', ]
def __dir__():
    return __all__


class Result(AbstractResult):

    def __init__(self, args=None, returncode=None, cpu_time=None, real_time=None, memory=None, gpu_time=None, gpu_memory=None, work_directory=None, environment=None, user=None, group=None, limits=None, stdin=None, stdout=None, stderr=None, status=None,):
        self._args = args and [str(a) for a in args] or []
        self._returncode = returncode and int(returncode) or 0
        self._cpu_time = None
        self.set_cpu_time(cpu_time)
        self._real_time = None
        self.set_real_time(real_time)
        self._memory = None
        self.set_memory(memory)
        self._gpu_time = None
        self.set_gpu_time(gpu_time)
        self._gpu_memory = None
        self.set_gpu_memory(gpu_memory)
        self._work_directory = work_directory and str(pathlib.Path(work_directory))
        self._environment = environment or dict()
        self._user = user and str(user)
        self._group = group and str(group)
        self._limits = limits or get_limits()
        self._stdin = stdin and pathlib.Path(stdin)
        self._stdout = stdout and pathlib.Path(stdout)
        self._stderr = stderr and pathlib.Path(stderr)
        self._status = status

    def __repr__(self):
        repr_dict = dict()
        for k,v in self.__dict__.items():
            if v is None:
                continue
            if k in [ '_system', '_name' ]:
                continue
            if len(k) and k[0] == '_':
                k=k[1:]
            if k.endswith('time'):
                repr_dict[k] = unparse_time(v)
            elif k.endswith('memory'):
                repr_dict[k] = unparse_memory(v)
            else:
                repr_dict[k] = repr(v)
        rep = f'{self.__class__.__name__}: {repr_dict}'
        return rep

    @property
    def yaml(self):
        yaml = nononedict()
        yaml['status'] = self.status
        yaml['args'] = self.args
        yaml['returncode'] = self.returncode
        yaml['user'] = self.user
        yaml['group'] = self.group
        yaml['work_directory'] = self.work_directory
        yaml['environment'] = self.environment
        yaml['limits'] = self.limits and self.limits.yaml or None
        if self.stdin and str(self.stdin) != '/dev/null':
            yaml['stdin'] = self.stdin
        if self.stdout and str(self.stdout) != '/dev/null':
            yaml['stdout'] = self.stdout
        if self.stderr and str(self.stderr) != '/dev/null':
            yaml['stderr'] = self.stderr
        yaml['cpu_time'] = unparse_time(self.cpu_time)
        yaml['real_time'] = unparse_time(self.real_time)
        yaml['memory'] = unparse_memory(self.memory)
        yaml['gpu_time'] = unparse_time(self.gpu_time)
        yaml['gpu_memory'] = unparse_memory(self.gpu_memory)
        return OrderedDict(yaml)

    @property
    def args(self):
        return self.get_args()
    def get_args(self):
        return self._args

    @property
    def returncode(self):
        return self.get_returncode()
    def get_returncode(self):
        return self._returncode
    def set_returncode(self, returncode):
        self._returncode = returncode and int(returncode) or 0

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
    def stderr(self):
        return self.get_stderr()
    def get_stderr(self):
        return self._stderr

    @property
    def cpu_time(self):
        return self.get_cpu_time()
    def get_cpu_time(self):
        return self._cpu_time
    def set_cpu_time(self, cpu_time):
        self._cpu_time = parse_time(cpu_time or '0s')
    def update_cpu_time(self, cpu_time):
        self._cpu_time = max(self._cpu_time, parse_time(cpu_time or '0s'))

    @property
    def real_time(self):
        return self.get_real_time()
    def get_real_time(self):
        return self._real_time
    def set_real_time(self, real_time):
        self._real_time = parse_time(real_time or '0s')
    def update_real_time(self, real_time):
        self._real_time = max(self._real_time, parse_time(real_time or '0s'))

    @property
    def memory(self):
        return self.get_memory()
    def get_memory(self):
        return self._memory
    def set_memory(self, memory):
        self._memory = parse_memory(memory or '0b')
    def update_memory(self, memory):
        self._memory = max(self._memory, parse_memory(memory or '0b'))

    @property
    def gpu_time(self):
        return self.get_gpu_time()
    def get_gpu_time(self):
        return self._gpu_time
    def set_gpu_time(self, gpu_time):
        self._gpu_time = parse_time(gpu_time or '0s')
    def update_gpu_time(self, gpu_time):
        self._gpu_time = max(self._gpu_time, parse_time(gpu_time or '0s'))

    @property
    def gpu_memory(self):
        return self.get_gpu_memory()
    def get_gpu_memory(self):
        return self._gpu_memory
    def set_gpu_memory(self, gpu_memory):
        self._gpu_memory = parse_memory(gpu_memory or '0b')
    def update_gpu_memory(self, gpu_memory):
        self._gpu_memory = max(self._gpu_memory, parse_memory(gpu_memory or '0b'))

    @property
    def status(self):
        return self.get_status()
    def get_status(self):
        return self._status
    def set_status(self, status):
        self._status = status


class ResultDict:
    def __init__(self):
        self._dict = OrderedDict()
        self._status = None
        pass
    def __repr__(self):
        return f'{self.__class__.__name__}: {self._status} {self._dict}'

    def __getattr__(self, key):
        return self._dict[key]
    def __getitem__(self, key):
        return self._dict[key]
    def set(self, key, val):
        assert key != 'status'
        assert key not in self._dict
        assert isinstance(key, str) or isinstance(key, int)
        if val is None:
            return
        assert isinstance(val, Result) or isinstance(val, ResultDict) or isinstance(val, str) or isinstance(val, int) or isinstance(val, float) or isinstance(val, pathlib.Path)
        self._dict[key] = val
    @property
    def status(self):
        return self.get_status()
    def get_status(self):
        return self._status
    def set_status(self, status):
        self._status = status
    @property
    def yaml(self):
        yaml = nononedict()
        yaml['status'] = self.status
        for key, val in self._dict.items():
            if isinstance(val, str) or isinstance(val, int) or isinstance(val, float) or isinstance(val, pathlib.Path):
                yaml[key] = val
            else:
                yaml[key] = val.yaml or None
        return OrderedDict(yaml)
    def items(self):
        ret = list()
        ret.append(('status', self.status))
        for key, val in self._dict.items():
            ret.append((key,val))
        return ret


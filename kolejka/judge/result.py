# vim:ts=4:sts=4:sw=4:expandtab
import datetime
import pathlib

from kolejka.judge import config
from kolejka.judge.parse import *
from kolejka.judge.typing import *


__all__ = [ 'Result', ]
def __dir__():
    return __all__


class Result(AbstractResult):

    def __init__(self, args=None, returncode=None, cpu_time=None, real_time=None, memory=None, work_directory=None, environment=None, user=None, group=None, limits=None, stdin=None, stdout=None, stderr=None,):
        self._args = args and [str(a) for a in args] or []
        self._returncode = returncode and int(returncode) or 0
        self._cpu_time = None
        self.set_cpu_time(cpu_time)
        self._real_time = None
        self.set_real_time(real_time)
        self._memory = None
        self.set_memory(memory)
        self._work_directory = work_directory and str(pathlib.Path(work_directory))
        self._environment = environment or dict()
        self._user = user and str(user)
        self._group = group and str(group)
        self._limits = limits or get_limits()
        self._stdin = stdin and str(pathlib.Path(stdin))
        self._stdout = stdout and str(pathlib.Path(stdout))
        self._stderr = stderr and str(pathlib.Path(stderr))

    def __repr__(self):
        repr_dict = dict()
        for k,v in self.__dict__.items():
            if k in [ '_system', '_name' ]:
                continue
            if len(k) and k[0] == '_':
                k=k[1:]
            repr_dict[k] = repr(v)
        rep = f'{self.__class__.__name__}: {repr_dict}'
        return rep

    @property
    def args(self) -> List[str]:
        return self.get_args()
    def get_args(self):
        return _args

    @property
    def returncode(self) -> int:
        return self.get_returncode()
    def get_returncode(self):
        return self._returncode
    def set_returncode(self, returncode):
        self._returncode = returncode and int(returncode) or 0

    @property
    def work_directory(self) -> str:
        return self.get_work_directory()
    def get_work_directory(self):
        return self._work_directory

    @property
    def environment(self) -> Dict[str, str]:
        return self.get_environment()
    def get_environment(self):
        return self._environment

    @property
    def user(self) -> Optional[str]:
        return self.get_user()
    def get_user(self):
        return self._user

    @property
    def group(self) -> Optional[str]:
        return self.get_group()
    def get_group(self):
        return self._group

    @property
    def limits(self) -> AbstractLimits:
        return self.get_limits()
    def get_limits(self):
        return self._limits

    @property
    def stdin(self) -> str:
        return self.get_stdin()
    def get_stdin(self):
        return self.stdin
    @property
    def stdout(self) -> str:
        return self.get_stdout()
    def get_stdout(self):
        return self.stdout
    @property
    def stderr(self) -> str:
        return self.get_stderr()
    def get_stderr(self):
        return self.stderr

    @property
    def cpu_time(self) -> datetime.timedelta:
        return self.get_cpu_time()
    def get_cpu_time(self):
        return self._cpu_time
    def set_cpu_time(self, cpu_time):
        self._cpu_time = parse_time(cpu_time or '0s')
    def update_cpu_time(self, cpu_time):
        self._cpu_time = max(self._cpu_time, parse_time(cpu_time or '0s'))

    @property
    def real_time(self) -> datetime.timedelta:
        return self.get_real_time()
    def get_real_time(self):
        return self._real_time
    def set_real_time(self, real_time):
        self._real_time = parse_time(real_time or '0s')
    def update_real_time(self, real_time):
        self._real_time = max(self._real_time, parse_time(real_time or '0s'))

    @property
    def memory(self) -> int:
        return self.get_memory()
    def get_memory(self):
        return self._memory
    def set_memory(self, memory):
        self._memory = parse_memory(memory or '0b')
    def update_memory(self, memory):
        self._memory = max(self._memory, parse_memory(memory or '0b'))

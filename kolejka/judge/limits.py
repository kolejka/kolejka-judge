# vim:ts=4:sts=4:sw=4:expandtab
import datetime
import sys
assert sys.version_info >= (3, 6)

from kolejka.judge.parse import *
from kolejka.judge.typing import *


__all__ = [ 'Limits', 'get_limits', ]
def __dir__():
    return __all__


class Limits(AbstractLimits):

    def __init__(self, cpu_time=None, real_time=None, memory=None, cores=None, pids=None):
        self._cpu_time = cpu_time and parse_time(cpu_time)
        self._real_time = real_time and parse_time(real_time)
        self._memory = memory and parse_memory(memory)
        self._cores = cores and int(cores)
        self._pids = pids and int(pids)

    @property
    def cpu_time(self) -> datetime.timedelta:
        return self.get_cpu_time()
    def get_cpu_time(self):
        return self._cpu_time
    def set_cpu_time(self, cpu_time):
        self._cpu_time = cpu_time and parse_time(cpu_time)
    def update_cpu_time(self, cpu_time):
        if not self.cpu_time:
            self.set_cpu_time(cpu_time)
        elif cpu_time:
            self._cpu_time = min(self._cpu_time, parse_time(cpu_time))

    @property
    def real_time(self) -> datetime.timedelta:
        return self.get_real_time()
    def get_real_time(self):
        return self._real_time
    def set_real_time(self, real_time):
        self._real_time = real_time and parse_time(real_time)
    def update_real_time(self, real_time):
        if not self.real_time:
            self.set_real_time(real_time)
        elif real_time:
            self._real_time = min(self._real_time, parse_time(real_time))

    @property
    def memory(self) -> int:
        return self.get_memory()
    def get_memory(self):
        return self._memory
    def set_memory(self, memory):
        self._memory = memory and parse_memory(memory)
    def update_memory(self, memory):
        if not self.memory:
            self.set_memory(memory)
        elif memory:
            self._memory = min(self._memory, parse_memory(memory))

    @property
    def cores(self) -> int:
        return self.get_cores()
    def get_cores(self):
        return self._cores
    def set_cores(self, cores):
        self._cores = cores and int(cores)
    def update_cores(self, cores):
        if not self.cores:
            self.set_cores(cores)
        elif cores:
            self._cores = min(self._cores, int(cores))

    @property
    def pids(self) -> int:
        return self.get_pids()
    def get_pids(self):
        return self._pids
    def set_pids(self, pids):
        self._pids = pids and int(pids)
    def update_pids(self, pids):
        if not self.pids:
            self.set_pids(pids)
        elif pids:
            self._pids = min(self._pids, int(pids))


def get_limits(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], Limits):
        return args[0]
    if len(args) == 1 and isinstance(args[0], dict):
        args[0].update(kwargs)
        return Limits(**args[0])
    if len(args) != 0:
        raise ValueError
    return Limits(**kwargs)

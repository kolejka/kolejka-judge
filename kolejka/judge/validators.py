# vim:ts=4:sts=4:sw=4:expandtab


from pathlib import Path
import re


from kolejka.judge import config
from kolejka.judge.parse import *


class ReturnCodePostcondition:
    def __init__(self, allowed_codes=None):
        self.allowed_codes = allowed_codes or [0]

    def __call__(self, system, result):
        return result.returncode in self.allowed_codes

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.allowed_codes))


class TimeLimitPostcondition:
    def __init__(self, cpu_time=None, real_time=None, gpu_time=None):
        self.cpu_time = parse_time(cpu_time)
        self.real_time = parse_time(real_time)
        self.gpu_time = parse_time(gpu_time)

    def __call__(self, system, result):
        return (
            ( self.cpu_time is None or result.cpu_time < self.cpu_time ) and
            ( self.real_time is None or result.real_time < self.real_time ) and
            ( self.gpu_time is None or result.gpu_time < self.gpu_time )
        )

    def __repr__(self):
        return '{}({},{},{})'.format(self.__class__.__name__, repr(self.cpu_time), repr(self.real_time), repr(self.gpu_time))


class MemoryLimitPostcondition:
    def __init__(self, memory=None, gpu_memory=None):
        self.memory = parse_memory(memory)
        self.gpu_memory = parse_memory(gpu_memory)

    def __call__(self, system, result):
        return (
            ( self.memory is None or result.memory < self.memory ) and
            ( self.gpu_memory is None or result.gpu_memory < self.gpu_memory )
        )

    def __repr__(self):
        return '{}({},{})'.format(self.__class__.__name__, repr(self.memory), repr(self.gpu_memory))


class EmptyErrorPostcondition:
    def __call__(self, system, result):
        if result.stderr is not None:
            return system.validators.file_empty(result.stderr)
        return True

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__)


class ParsedErrorPostcondition:
    def __init__(self, *args):
        self.disallowed_lines = [ re.compile(dl) for dl in args ]

    def __call__(self, system, result):
        if result.stderr is not None:
            return system.validators.file_does_not_match(result.stderr, self.disallowed_lines)
        return True

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.disallowed_lines))


class FileExistsPrerequirement:
    def __init__(self, path):
        self.path = path

    def __call__(self, system):
        if not self.path:
            return True
        return system.validators.file_exists(self.path)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.path))


class DirectoryExistsPrerequirement:
    def __init__(self, path):
        self.path = path

    def __call__(self, system):
        if not self.path:
            return True
        return system.validators.directory_exists(self.path)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.path))


class ProgramExistsPrerequirement:
    def __init__(self, path):
        self.path = path

    def __call__(self, system):
        if not self.path:
            return True
        return system.validators.program_exists(self.path)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.path))


class SystemProgramExistsPrerequirement:
    def __init__(self, path):
        self.path = path

    def __call__(self, system):
        if not self.path:
            return True
        return system.validators.system_program_exists(self.path)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.path))


class SystemUserExistsPrerequirement:
    def __init__(self, user=None):
        self.user = user

    def __call__(self, system):
        if not self.user:
            return True
        return system.validators.system_user_exists(self.user)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.user))


class SystemGroupExistsPrerequirement:
    def __init__(self, group=None):
        self.group = group

    def __call__(self, system):
        if not self.group:
            return True
        return system.validators.system_group_exists(self.group)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.group))

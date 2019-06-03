import re
from kolejka.judge.environments import ExecutionEnvironmentBase


class ExitCodePostcondition:
    def __init__(self, allowed_codes=None):
        self.allowed_codes = allowed_codes or [0]

    def __call__(self, result):
        return result.returncode in self.allowed_codes


class UsedTimePostcondition:
    def __init__(self, time):
        self.time = time

    def __call__(self, result):
        return result.stats.cpus['*'].usage.total_seconds() < self.time


class UsedMemoryPostcondition:
    def __init__(self, memory):
        self.memory = memory

    def __call__(self, result):
        return result.stats.memory.max_usage < self.memory


class PSQLErrorPostcondition:
    def __call__(self, result):
        if result.stderr is not None:
            with open(result.stderr, 'r') as stderr_file:
                # 87ccefd52b6a4c9a0d81df42c54535a2.py
                notice = re.compile('^.*ERROR:')
                for line in stderr_file:
                    if notice.match(line.rstrip()):
                        return False
        return True


class NonEmptyListPrerequisite:
    def __init__(self, lst):
        self.list = lst

    def __call__(self, environment: ExecutionEnvironmentBase):
        return len(self.list) > 0

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.list))


class FileExistsPrerequisite:
    def __init__(self, file):
        self.file = file

    def __call__(self, environment: ExecutionEnvironmentBase):
        return environment.validators.file_exists(self.file)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.file))


class ProgramExistsPrerequisite:
    def __init__(self, file):
        self.file = file

    def __call__(self, environment: ExecutionEnvironmentBase):
        return environment.validators.program_exists(self.file)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.file))


class FileOnARequiredListPrerequisite:
    def __init__(self, file):
        self.file = file

    def __call__(self, environment: ExecutionEnvironmentBase):
        return environment.validators.file_on_a_required_list(self.file)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.file))

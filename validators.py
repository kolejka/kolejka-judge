import os
import re
import shutil


class ExitCodePostcondition:
    def __init__(self, allowed_codes=None):
        self.allowed_codes = allowed_codes or [0]

    def __call__(self, result):
        return result.returncode in self.allowed_codes


class UsedTimePostcondition:
    def __init__(self, time):
        self.time = time

    def __call__(self, result):
        return result.stats.cpus['*'].usage < self.time


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


class FileExistsPrerequisite:
    def __init__(self, file):
        self.file = file

    def __call__(self, *args, **kwargs):
        return os.path.exists(self.file)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.file))


class ProgramExistsPrerequisite:
    def __init__(self, file):
        self.file = file

    def __call__(self, *args, **kwargs):
        return shutil.which(self.file) is not None

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.file))

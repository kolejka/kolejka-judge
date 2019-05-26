import os
from pathlib import Path
from stat import S_ISUID
from typing import Tuple, Optional

from tasks.base import Task


class CreateUser(Task):
    def __init__(self, username):
        self.username = username

    def execute(self, name, environment) -> Tuple[Optional[str], Optional[object]]:
        os.system("useradd {}".format(self.username))

        return None, None


class Setuid(Task):
    def __init__(self, file):
        self.file = Path(file)

    def execute(self, name, environment) -> Tuple[Optional[str], Optional[object]]:
        permissions = self.file.stat().st_mode
        self.file.chmod(permissions | S_ISUID)

        return None, None

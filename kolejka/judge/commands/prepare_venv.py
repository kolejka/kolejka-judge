from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *

__all__ = [
    'CreateVenvCommand',
]

class CreateVenvCommand(ProgramCommand):
    DEFAULT_PROGRAM='python3'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path 

    def get_program_arguments(self):
        args = ["-m", "venv", self.path]
        return args 
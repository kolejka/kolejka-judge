from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *

__all__ = ['RustcCommand']
def __dir__():
    return __all__


class CargoBuildCommand(CompileCommand):
    DEFAULT_PROGRAM='cargo'
    DEFAULT_BUILD_ARGUMENTS = ['build']
    
class RustcCommand(CompileCommand):
    DEFAULT_PROGRAM='rustc'
    
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def static(self):
        return False 
    
    def get_static(self):
        return False 
    
    @property
    def version(self):
        return self.get_version()
    
    def get_version(self):
        return None
    
    @property
    def standard(self):
        return self.get_standard()
    
    def get_standard(self):
        return self._standard
    
    def get_program(self):
        program = super().get_program()
        if self.version:
            program = program+'-'+str(self.version)
        return program

    def get_build_arguments(self):
        args = []
        return args + super().get_build_arguments()
    
    def get_library_arguments(self, library):
        return []
    
    def get_target_arguments(self, target):
        return [ '-o', target, ]
    
    def get_build_target(self):
        return super().get_build_target() or get_relative_path('a.out')
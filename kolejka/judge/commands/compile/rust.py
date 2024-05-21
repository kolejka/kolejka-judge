from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import *


__all__ = [
 'CargoNewCommand', 'CopySourceCommand', 'CargoBuildCommand',
 'MoveCommand', 'AddOfflineDependency'
]
def __dir__():
    return __all__

class AddOfflineDependency(ProgramCommand):
    DEFAULT_PROGRAM='cargo'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, project_path, dep_path, **kwargs):
        super().__init__(**kwargs)
        self.project_path = project_path
        self.dep_path = dep_path

    def get_program_arguments(self):
        args = ["add", "--offline", "--manifest-path", self.project_path, "--path", self.dep_path]
        return args 
    
    def get_environment(self):
        #FIXME: this is bad. 
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
        
        
        return super_result
    
class CargoNewCommand(ProgramCommand):
    DEFAULT_PROGRAM='cargo'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path 

    def get_program_arguments(self):
        args = ["new", self.path]
        return args 
    
    def get_environment(self):
        #FIXME: this is bad. 
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
                
        return super_result

class MoveCommand(ProgramCommand):
    DEFAULT_PROGRAM='mv'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, source, target, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.target = target
        
    def get_program_arguments(self):
        args = [self.source, self.target]
        return args

class CopySourceCommand(ProgramCommand):
    DEFAULT_PROGRAM='cp'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, source, target, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.target = target
        
    def get_program_arguments(self):
        args = ["-rf", f"{self.source}/.", self.target]
        return args
    
class CargoBuildCommand(CompileCommand):
    DEFAULT_PROGRAM='cargo'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, cargo_config_file, **kwargs):
        super().__init__(**kwargs)
        self.cargo_config_file = cargo_config_file

    def get_environment(self):
        #FIXME: this is bad. 
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
                
        return super_result
    
    def get_program_arguments(self):
        args = ["build", "--manifest-path", self.cargo_config_file]
        return args
    
    def get_program(self):
        program = super().get_program()
        return program

    def get_build_arguments(self):
        args = []
        return args + super().get_build_arguments()
    
    def get_library_arguments(self, library):
        return []
    
    def get_target_arguments(self, target):
        return []
    
    def get_build_target(self):
        return super().get_build_target() or get_relative_path('a.out')


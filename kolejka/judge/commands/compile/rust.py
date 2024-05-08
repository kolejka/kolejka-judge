from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import *


__all__ = ['RustcCommand', 'CargoNewCommand', 'CopySourceCommand', 'CargoBuildCommand']
def __dir__():
    return __all__
    
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
        print("GET ENVIRONMENT")
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
        
        print("environment", super_result)
        
        return super_result

class CopySourceCommand(ProgramCommand):
    DEFAULT_PROGRAM='cp'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, source, target, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.target = target
        
    def get_program_arguments(self):
        args = ["-r", self.source, self.target]
        return args
    
class CargoBuildCommand(ProgramCommand):
    DEFAULT_PROGRAM='cargo'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def get_environment(self):
        #FIXME: this is bad. 
        print("GET ENVIRONMENT")
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
        
        print("environment", super_result)
        
        return super_result
    
    def get_program_arguments(self):
        args = ["build", "--manifest-path", self.target]
        return args
        
        
class RustcCommand(CompileCommand):
    DEFAULT_PROGRAM='rustc'
    
    @default_kwargs
    def __init__(self, **kwargs):
        print("RUSTC COMMAND")
        print(kwargs)
        super().__init__(**kwargs)

    def get_environment(self):
        #FIXME: this is bad. 
        print("GET ENVIRONMENT")
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
        
        print("environment", super_result)
        
        return super_result

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
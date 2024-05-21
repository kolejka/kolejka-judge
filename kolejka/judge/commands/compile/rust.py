from kolejka.judge import config
from kolejka.judge.commands.compile.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands.base import *


__all__ = [
    'RustcCommand', 'CargoNewCommand', 'CopySourceCommand',
    'CargoBuildCommand', 'MoveCommand', 'CreateDirectoryCommand', 'AddOfflineDependency']
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

class CreateDirectoryCommand(ProgramCommand):
    DEFAULT_PROGRAM='mkdir'
    DEFAULT_SAFE=True
    
    @default_kwargs
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path 

    def get_program_arguments(self):
        args = ["-p", self.path]
        return args

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
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def get_environment(self):
        #FIXME: this is bad. 
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
                
        return super_result
    
    def get_program_arguments(self):
        args = ["build", "--manifest-path", self.target]
        return args

class RustcCommand(CompileCommand):
    DEFAULT_PROGRAM='true' # FIXME: haha
    
    @default_kwargs
    def __init__(self, **kwargs):
        print("RUSTC COMMAND")
        print(kwargs)
        super().__init__(**kwargs)

    def get_environment(self):
        #FIXME: this is bad. 
        super_result = super().get_environment()
        
        super_result['RUSTUP_HOME'] = '/home/dominik/.rustup'
        super_result['CARGO_HOME'] = '/home/dominik/.cargo'
                
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
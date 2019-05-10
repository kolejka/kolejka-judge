from pathlib import Path

from commands.base import CommandBase
from commands.compile.asm import CompileNasm
from commands.compile.c_cpp import CompileCpp, CompileC
from commands.compile.csharp import CompileCSharp
from commands.compile.go import CompileGo
from commands.compile.haskell import CompileHaskell
from commands.compile.java import CompileJava
from validators import FileExistsPrerequisite


class AutoCompile(CommandBase):
    def __init__(self, file, **kwargs):
        limits = kwargs.pop('limits', None)
        super().__init__(limits=limits)
        self.file = file
        compiler_cls = self.detect_compiler(file)
        self.compiler = compiler_cls(file, **kwargs) if compiler_cls else None

    def detect_compiler(self, file):
        known_compilers = {
            'asm': CompileNasm,
            'c': CompileC,
            'cpp': CompileCpp,
            'cs': CompileCSharp,
            'hs': CompileHaskell,
            'java': CompileJava,
            'go': CompileGo,
        }

        ext = Path(file).suffix[1:]
        if ext not in known_compilers:
            return None

        return known_compilers[ext]

    def get_configuration_status(self):
        return (True, None) if self.compiler is not None else (False, 'EXT')

    def get_command(self):
        return self.compiler.get_command()

    def prerequisites(self):
        return self.compiler.prerequisites() + [FileExistsPrerequisite(self.file)]

    def postconditions(self):
        return self.compiler.postconditions()

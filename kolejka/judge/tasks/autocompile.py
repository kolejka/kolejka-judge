from pathlib import Path
from typing import Optional, Dict, Type, Tuple

from kolejka.judge.commands.base import CommandBase
from kolejka.judge.commands.compile.c_cpp import CompileCpp, CompileC
from kolejka.judge.commands.compile.csharp import CompileCSharp
from kolejka.judge.commands.compile.go import CompileGo
from kolejka.judge.commands.compile.haskell import CompileHaskell
from kolejka.judge.commands.compile.java import CompileJava
from kolejka.judge.environments import ExecutionEnvironment
from kolejka.judge.tasks.base import Task


class AutoCompileTask(Task):
    def __init__(self, file, **kwargs):
        self.file = file
        self.kwargs = kwargs

    @staticmethod
    def detect_step(file) -> Optional[Type[CommandBase]]:
        known_steps: Dict[str, Type[CommandBase]] = {
            'c': CompileC,
            'cpp': CompileCpp,
            'cs': CompileCSharp,
            'hs': CompileHaskell,
            'java': CompileJava,
            'go': CompileGo,
        }

        ext = Path(file).suffix[1:]
        if ext not in known_steps:
            return None

        return known_steps[ext]

    @staticmethod
    def detect_run_command(file):
        stem = Path(file).stem
        commands = {
            'c': './a.out',
            'cpp': './a.out',
            'cs': 'mono main.exe',
            'hs': './{}'.format(stem),
            'java': 'java {}'.format(stem),
            'go': './a.out',
        }

        ext = Path(file).suffix[1:]
        return commands[ext]

    def execute(self, name, environment: ExecutionEnvironment) -> Tuple[Optional[str], Optional[object]]:
        step_cls = self.detect_step(self.file)
        if step_cls is None:
            return 'EXT', None

        step = step_cls(self.file, **self.kwargs)
        result = environment.run_command_step(step, name='autocompile_{}'.format(name))

        shell_file_path = environment.get_path(Path('autocompile/run.sh'))
        shell_file = environment.get_file_handle(shell_file_path, 'w')
        shell_file.write("#!/bin/sh\n")
        shell_file.write(self.detect_run_command(self.file))
        shell_file.write(" <&0 >&1 2>&2")
        shell_file.close()
        shell_file_path.chmod(0o777)

        return result

    def prerequisites(self):
        step_cls = self.detect_step(self.file)
        if step_cls is not None:
            step = step_cls(self.file, **self.kwargs)
            return step.prerequisites()

        return []

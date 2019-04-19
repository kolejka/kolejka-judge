from typing import List

from commands.compile.base import CompileBase


class CompileCSharp(CompileBase):
    def __init__(self, *args: str, compiler='mcs', compilation_options: List[str] = None, **kwargs):
        compilation_options = compilation_options or ['-t:exe', '-out:main.exe']
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)


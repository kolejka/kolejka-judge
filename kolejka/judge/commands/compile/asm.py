from typing import List

from kolejka.judge.commands.compile.base import CompileBase


class CompileNasm(CompileBase):
    def __init__(self, *args: str, compiler='nasm', compilation_options: List[str] = None, **kwargs):
        compilation_options = compilation_options or ['-felf64']
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)

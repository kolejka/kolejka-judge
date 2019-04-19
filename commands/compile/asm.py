from typing import List

from commands.compile.base import CompileBase


class CompileNasm(CompileBase):
    def __init__(self, *args: str, compiler='nasm', compilation_options: List[str] = None, **kwargs):
        compilation_options = compilation_options or ['-felf64']
        super().__init__(*args, compiler=compiler, compilation_options=compilation_options, **kwargs)

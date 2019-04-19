from typing import List

from commands.compile.base import CompileBase


class CompileGo(CompileBase):
    def __init__(self, *args: str, compiler='gccgo', compilation_options: List[str] = None, **kwargs):
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)

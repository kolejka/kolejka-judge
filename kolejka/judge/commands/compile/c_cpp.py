from typing import List

from kolejka.judge.commands.compile.base import CompileBase


class CompileC(CompileBase):
    def __init__(self, *args: str, compiler='gcc', compilation_options: List[str] = None, **kwargs):
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)


class CompileCpp(CompileBase):
    def __init__(self, *args: str, compiler='g++', compilation_options: List[str] = None, **kwargs):
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)

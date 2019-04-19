from typing import List

from commands.compile.base import CompileBase


class CompileHaskell(CompileBase):
    def __init__(self, *args: str, compiler='ghc', compilation_options: List[str] = None, **kwargs):
        super().__init__(compiler, *args, compilation_options=compilation_options, **kwargs)

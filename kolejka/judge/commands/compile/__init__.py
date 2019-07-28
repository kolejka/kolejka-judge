# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.commands.compile.base import *
from kolejka.judge.commands.compile.gcc import *
from kolejka.judge.commands.compile.ghc import *
from kolejka.judge.commands.compile.mono import *
from kolejka.judge.commands.compile.nasm import *

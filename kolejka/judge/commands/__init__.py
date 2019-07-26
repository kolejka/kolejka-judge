# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.commands.base import *
from kolejka.judge.commands.check import *
from kolejka.judge.commands.compile import *
from kolejka.judge.commands.db import *
from kolejka.judge.commands.extract import *
from kolejka.judge.commands.make import *
from kolejka.judge.commands.system import *

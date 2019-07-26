# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)

from kolejka.judge.tasks.build import *
from kolejka.judge.tasks.check import *
from kolejka.judge.tasks.prepare import *
from kolejka.judge.tasks.rules import *
from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.system import *
from kolejka.judge.tasks.tools import *

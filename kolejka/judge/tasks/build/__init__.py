# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)

from kolejka.judge.tasks.build.base import *
from kolejka.judge.tasks.build.auto import *
from kolejka.judge.tasks.build.make import *
from kolejka.judge.tasks.build.compile import *

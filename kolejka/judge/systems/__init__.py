# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.systems.local import *
from kolejka.judge.systems.psutil import *
from kolejka.judge.systems.observer import *
from kolejka.judge.systems.systemd import *

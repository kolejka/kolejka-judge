import json

from checking import Checking
from commands.compile.make import CMake, Make
from commands.check import Diff
from commands.run.base import RunSolution
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    cmake=CMake(),
    make=Make(build_dir='build'),
    solution=RunSolution(executable='build/untitled', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

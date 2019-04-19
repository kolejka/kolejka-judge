from checking import Checking
from environments import *
from commands.compile.make import CMake, Make
from commands.diff import Diff
from commands.run.base import RunSolution


checking = Checking(environment=LocalComputer())
checking = Checking(environment=KolejkaObserver())
checking.add_steps(
    cmake=CMake(),
    make=Make(build_dir='build'),
    solution=RunSolution(executable='build/untitled', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

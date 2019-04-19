from checking import Checking
from environments import *
from commands.compile.go import CompileGo
from commands.diff import Diff
from commands.run.base import RunSolution

checking = Checking(environment=LocalComputer())
checking = Checking(environment=KolejkaObserver())
checking.add_steps(
    compile=CompileGo('**/*.go'),
    solution=RunSolution('./a.out', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

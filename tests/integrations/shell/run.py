from checking import Checking
from environments import *
from commands.diff import Diff
from commands.run.shell import RunShellSolution

checking = Checking(environment=LocalComputer())
checking = Checking(environment=KolejkaObserver())
checking.add_steps(
    run=RunShellSolution('./solution.sh', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

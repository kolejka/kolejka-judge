import json

from checking import Checking
from commands.diff import Diff
from commands.run.shell import RunShellSolution
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    run=RunShellSolution('./solution.sh', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

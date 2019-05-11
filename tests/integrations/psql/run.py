import json

from checking import Checking
from commands.check import Diff
from commands.run.db import RunPSQLSolution
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    run=RunPSQLSolution('solution.sql', stdout='out', cmdline_options=['-qAt'],
                        user='test', host='localhost', password='test', database='test'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

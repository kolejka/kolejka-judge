import json

from kolejka.judge.checking import Checking
from kolejka.judge.commands.check import Diff
from kolejka.judge.commands.run.db import RunPSQLSolution
from kolejka.judge.utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    run=RunPSQLSolution('solution.sql', stdout='out', cmdline_options=['-qAt'],
                        db_user='test', host='localhost', db_password='test', database='test'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

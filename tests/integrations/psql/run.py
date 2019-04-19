from checking import Checking
from environments import *
from commands.diff import Diff
from commands.run.db import RunPSQLSolution

checking = Checking(environment=LocalComputer())
checking = Checking(environment=KolejkaObserver())
checking.add_steps(
    run=RunPSQLSolution('solution.sql', stdout='out', cmdline_options=['-qAt'],
                        user='test', host='localhost', password='test', database='test'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

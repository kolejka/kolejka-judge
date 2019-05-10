import json

from checking import Checking
from commands.check import Diff
from commands.extract import ExtractArchive
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    extract=ExtractArchive('solution.zip', directory='extract'),
    diff=Diff('extract/solution.txt', 'wzo'),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

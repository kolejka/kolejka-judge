import json

from checking import Checking
from commands.compile.haskell import CompileHaskell
from commands.check import Diff
from commands.run.base import RunSolution
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    compile=CompileHaskell('**/*.hs', compilation_options=['-o', 'main']),
    solution=RunSolution('./main', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

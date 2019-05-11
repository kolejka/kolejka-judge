import json

from checking import Checking
from commands.compile.csharp import CompileCSharp
from commands.check import Diff
from commands.run.csharp import RunCSharpSolution
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    compile=CompileCSharp('**/*.cs'),
    solution=RunCSharpSolution('main.exe', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

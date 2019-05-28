import json

from kolejka.judge.checking import Checking
from kolejka.judge.commands.compile.csharp import CompileCSharp
from kolejka.judge.commands.check import Diff
from kolejka.judge.commands.run.csharp import RunCSharpSolution
from kolejka.judge.utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    compile=CompileCSharp('**/*.cs'),
    solution=RunCSharpSolution('main.exe', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

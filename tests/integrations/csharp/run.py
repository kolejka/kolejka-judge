from checking import Checking
from environments import *
from commands.compile.csharp import CompileCSharp
from commands.diff import Diff
from commands.run.csharp import RunCSharpSolution

checking = Checking(environment=LocalComputer())
checking = Checking(environment=KolejkaObserver())
checking.add_steps(
    compile=CompileCSharp('**/*.cs'),
    solution=RunCSharpSolution('main.exe', stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

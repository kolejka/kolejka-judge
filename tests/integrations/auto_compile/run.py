import json

from kolejka.judge.checking import Checking
from kolejka.judge.commands.check import RunChecker
from kolejka.judge.commands.compile.java import CompileJava
from kolejka.judge.commands.run.java import RunJavaClassSolution
from kolejka.judge.tasks.autocompile import AutoCompile
from kolejka.judge.utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    compile_checker=AutoCompile('checker.cpp'),
    compile_solution=CompileJava('Solution.java'),
    solution=RunJavaClassSolution(class_name='Solution', stdout='out'),
    check=RunChecker('autocompile/run.sh', stdin='out'),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

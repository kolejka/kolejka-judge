import json

from checking import Checking
from commands.check import RunChecker
from commands.compile.java import CompileJava
from commands.run.java import RunJavaClassSolution
from tasks.autocompile import AutoCompileTask
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    compile_checker=AutoCompileTask('checker.cpp'),
    compile_solution=CompileJava('Solution.java'),
    solution=RunJavaClassSolution(class_name='Solution', stdout='out'),
    check=RunChecker('autocompile/run.sh', stdin='out'),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

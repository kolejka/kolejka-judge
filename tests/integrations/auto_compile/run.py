import json

from checking import Checking
from commands.check import RunChecker
from commands.compile.detect import AutoCompile
from commands.run.java import RunJavaClassSolution
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    compile_checker=AutoCompile('checker.cpp', compilation_options=['-o', 'checker']),
    compile_solution=AutoCompile('Solution.java'),
    solution=RunJavaClassSolution(class_name='Solution', stdout='out'),
    check=RunChecker('./checker', stdin='out'),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

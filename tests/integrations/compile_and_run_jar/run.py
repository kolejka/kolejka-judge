import json

from checking import Checking
from commands.compile.java import CompileJava, CreateJar
from commands.check import Diff
from commands.run.java import RunJarSolution
from environments import DependentExpr
from tasks.java import RenameJavaFileTask
from tasks.list import ListFilesTask
from utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    rename=RenameJavaFileTask('solution.java'),
    list_jars=ListFilesTask('**/*.jar', variable_name='jars'),
    compile=CompileJava('**/*.java', compilation_options=[
        '-cp',
        DependentExpr('jars', func=lambda x: '.:' + ':'.join(x))
    ]),
    create_jar=CreateJar('**/*.class', entrypoint='Main'),
    run_jar=RunJarSolution(interpreter_options=[
        DependentExpr('jars', func=lambda x: '-Xbootclasspath/a:' + ':'.join(x))
    ], stdout='out'),
    diff=Diff(),
)
status, res = checking.run()
print(json.dumps(checking.format_result(res), indent=4))
print(status)

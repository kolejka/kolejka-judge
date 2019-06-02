import json

from kolejka.judge.checking import Checking
from kolejka.judge.commands.compile.java import CompileJava, CreateJar
from kolejka.judge.commands.check import Diff
from kolejka.judge.commands.run.java import RunJarSolution
from kolejka.judge.lazy import DependentExpr
from kolejka.judge.tasks.java import RenameJavaFile
from kolejka.judge.tasks.list_files import ListFiles
from kolejka.judge.utils import detect_environment

checking = Checking(environment=detect_environment())
checking.add_steps(
    rename=RenameJavaFile('solution.java'),
    list_jars=ListFiles('**/*.jar', variable_name='jars'),
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

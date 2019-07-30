# vim:ts=4:sts=4:sw=4:expandtab
import pathlib


from kolejka.judge import config
from kolejka.judge.ctxyaml import *
from kolejka.judge.parse import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *


__all__ = [ 'commit_task', ]
def __dir__():
    return __all__


def commit_task(task_dir, tests, solution, runpy):

    kolejka_image = 'kolejka/satori:judge'
    kolejka_requires = []
    kolejka_exclusive = True
    kolejka_limits = {}
    kolejka_stdout = 'console_stdout.txt'
    kolejka_stderr = 'console_stderr.txt'
    kolejka_collect = []

    kolejka_system = '--local'

    from kolejka.common import KolejkaTask, KolejkaLimits
    task_dir = pathlib.Path(task_dir).resolve()
    solution = pathlib.Path(solution).resolve()
    runpy = pathlib.Path(runpy).resolve()
    
    task_dir.mkdir(parents=True)
    test_dir = pathlib.PurePath('tests')
    (task_dir/test_dir).mkdir()
    solution_dir = pathlib.PurePath('solution')
    (task_dir/solution_dir).mkdir()
    results_dir = pathlib.PurePath('results')
    results_yaml = pathlib.PurePath('results.yaml')

    kolejka_collect += [{'glob' : str(results_dir/results_yaml)}]
    kolejka_collect += [{'glob' : str(results_dir / '**' / config.LOG / '*')}]

    tests_yaml = test_dir / 'tests.yaml'
    solution_path = solution_dir / solution.name
    (task_dir/solution_path).symlink_to(solution)
    runpy_path = pathlib.PurePath('run.py')
    (task_dir/runpy_path).symlink_to(runpy)
    lib_path = pathlib.PurePath('KolejkaJudge.zip')
    (task_dir/lib_path).symlink_to(runpy.parent / lib_path)

    task_args = [ 'python3', 'run.py', kolejka_system, '--tests', str(tests_yaml), '--solution', str(solution_path), '--output-directory', str(results_dir), '--results', str(results_yaml), ]

    input_map = dict()
    class collect:
        def __init__(self, input_map):
            self.input_count = 0
            self.input_map = input_map
        def __call__(self, a):
            if isinstance(a, pathlib.Path):
                if a in self.input_map:
                    return self.input_map[a]
                self.input_count += 1
                input_path = task_dir / test_dir / ('%03d'%(self.input_count,)) / a.name
                input_path.parent.mkdir(exist_ok=True, parents=True)
                input_path.symlink_to(a)
                input_path = input_path.relative_to(task_dir)
                self.input_map[a] = input_path
                return input_path
            if isinstance(a, list):
                return [ self(e) for e in a ]
            if isinstance(a, dict):
                return dict( [ (self(k), self(v)) for k,v in a.items() ] )
            return a
    tests = collect(input_map)(tests)
    ctxyaml_dump(tests, task_dir, task_dir/tests_yaml)

    task = KolejkaTask(
            str(task_dir),
            image = kolejka_image,
            requires = kolejka_requires,
            exclusive = kolejka_exclusive,
            limits = kolejka_limits,
            args = task_args,
            stdout = kolejka_stdout,
            stderr = kolejka_stderr,
            files = dict([ (str(p), None) for p in
                    [ tests_yaml, solution_path, runpy_path, lib_path, ]
                    + list(input_map.values())
                ]),
            collect = kolejka_collect,
            )
    task.commit()


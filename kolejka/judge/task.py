# vim:ts=4:sts=4:sw=4:expandtab


import datetime
import logging
import pathlib


from kolejka.judge import config
from kolejka.judge.ctxyaml import ctxyaml_dump
from kolejka.judge.parse import parse_time, parse_memory
from kolejka.judge.paths import InputPath


__all__ = [ 'kolejka_task', ]
def __dir__():
    return __all__


def kolejka_task(task_dir, tests, solution, judgepy, exist_ok=False, debug=False):

    kolejka_image = None
    kolejka_requires = set()
    kolejka_exclusive = False
    kolejka_collects = dict()
    kolejka_stdout = 'console_stdout.txt'
    kolejka_stderr = 'console_stderr.txt'
    kolejka_limits = {}

    kolejka_system = '--observer'

    for test_id, test in tests.items():
        kolejka_opts = test.get('kolejka', dict())

        if 'image' in kolejka_opts:
            if kolejka_image and kolejka_image != kolejka_opts['image']:
                raise ValueError
            kolejka_image = kolejka_opts['image']
        for req in kolejka_opts.get('requires', []):
            kolejka_requires.add(req)
        kolejka_exclusive = kolejka_exclusive or bool(kolejka_opts.get('exclusive', False))
        kolejka_collects[test_id] = kolejka_opts.get('collect', [])
        kolejka_collects[test_id].append(config.SATORI_RESULT+'/**')
        test_limits = kolejka_opts.get('limits', {})
        if 'time' in test_limits:
            kolejka_limits['time'] = kolejka_limits.get('time', datetime.timedelta(seconds=1)) + parse_time(test_limits['time'])
        if 'memory' in test_limits:
            kolejka_limits['memory'] = max(kolejka_limits.get('memory', 0), parse_memory(test_limits['memory']))
        if 'swap' in test_limits:
            kolejka_limits['swap'] = max(kolejka_limits.get('swap', 0), parse_memory(test_limits['swap']))
        if 'cpus' in test_limits:
            kolejka_limits['cpus'] = max(kolejka_limits.get('cpus', 1), int(test_limits['cpus']))
        if 'network' in test_limits:
            kolejka_limits['network'] = kolejka_limits.get('network', False) or bool(test_limits['network'])
        if 'pids' in test_limits:
            kolejka_limits['pids'] = max(kolejka_limits.get('pids', 16), int(test_limits['pids']))
        if 'storage' in test_limits:
            kolejka_limits['storage'] = kolejka_limits.get('storage', 0) + parse_memory(test_limits['storage'])
        if 'workspace' in test_limits:
            kolejka_limits['workspace'] = kolejka_limits.get('workspace', 0) + parse_memory(test_limits['workspace'])

    kolejka_image = kolejka_image or 'kolejka/satori:judge'

    from kolejka.common import KolejkaTask, KolejkaLimits
    task_dir = pathlib.Path(task_dir).resolve()
    solution = pathlib.Path(solution).resolve()
    judgepy = pathlib.Path(judgepy).resolve()
    
    task_dir.mkdir(parents=True, exist_ok=exist_ok)
    test_dir = pathlib.PurePath('tests')
    (task_dir/test_dir).mkdir()
    solution_dir = pathlib.PurePath('solution')
    (task_dir/solution_dir).mkdir()
    results_dir = pathlib.PurePath('results')
    results_yaml = pathlib.PurePath('results.yaml')

    kolejka_collect = []
    kolejka_collect += [{'glob' : str(results_dir/results_yaml)}]
    for test_id, collects in kolejka_collects.items():
        for collect in collects:
            kolejka_collect += [{'glob' : str(results_dir / str(test_id) / str(collect))}]
    if debug:
        kolejka_collect += [
                {'glob' : str(test_dir) + '/**'},
                {'glob' : str(solution_dir) + '/**'},
                {'glob' : str(results_dir) + '/**'},
            ]

    tests_yaml = test_dir / 'tests.yaml'
    solution_path = solution_dir / solution.name
    (task_dir/solution_path).symlink_to(solution)
    judgepy_path = pathlib.PurePath('judge.py')
    (task_dir / judgepy_path).symlink_to(judgepy)
    lib_path = pathlib.PurePath(config.DISTRIBUTION_PATH)
    (task_dir / lib_path).symlink_to(judgepy.parent / lib_path)
    if not (judgepy.parent / lib_path).is_file():
        logging.warning('Kolejka Judge library not present in {}. Try running library update.'.format(judgepy.parent / lib_path))


    task_args = [ 'python3', str(judgepy_path), ]
    if debug:
        task_args += [ '--debug', ]
    task_args += [ 'execute', kolejka_system, str(tests_yaml), str(solution_path), str(results_dir), '--results', str(results_yaml), ]

    input_map = dict()
    class collect:
        def __init__(self, input_map):
            self.input_count = 0
            self.input_map = input_map
        def __call__(self, a):
            if isinstance(a, InputPath):
                a = pathlib.Path(a.path)
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
    ctxyaml_dump(tests, task_dir/tests_yaml, work_dir=task_dir)

    task = KolejkaTask(
            str(task_dir),
            image = kolejka_image,
            requires = list(kolejka_requires),
            exclusive = kolejka_exclusive,
            limits = kolejka_limits,
            args = task_args,
            stdout = kolejka_stdout,
            stderr = kolejka_stderr,
            files = dict([ (str(p), None) for p in
                    [ tests_yaml, solution_path, judgepy_path, lib_path, ]
                    + list(input_map.values())
                ]),
            collect = kolejka_collect,
            )
    task.commit()


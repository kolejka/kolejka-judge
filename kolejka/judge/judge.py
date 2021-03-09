# vim:ts=4:sts=4:sw=4:expandtab


import argparse
import logging
import pathlib
import shutil
import subprocess
import tempfile
import urllib.request


from kolejka.judge import config
from kolejka.judge.checking import Checking
from kolejka.judge.ctxyaml import ctxyaml_load, ctxyaml_dump
from kolejka.judge.paths import get_input_path
from kolejka.judge.task import kolejka_task


__all__ = [ 'config_parser', 'config_parser_update', 'config_parser_task', 'config_parser_client', 'config_parser_execute', ]
def __dir__():
    return __all__


class RelativePathAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self.type = pathlib.Path
        if nargs is not None:
            raise ValueError('nargs not allowed.')
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        parts = list()
        try:
            for part in pathlib.PurePath(values).parts:
                if part == '..':
                    parts.pop()
                parts.append(part)
        except (IndexError, TypeError):
            parser.error('\'{}\' is not a relative path.'.format(values))
        path = pathlib.Path(*parts)
        setattr(namespace, self.dest, path)


class ExistingFileAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self.type = pathlib.Path
        if nargs is not None:
            raise ValueError('nargs not allowed.')
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        path = pathlib.Path(values)
        if not path.exists():
            parser.error('{} \'{}\' does not exist.'.format(self.dest.title(), path))
        if not path.is_file():
            parser.error('{} \'{}\' is not a file.'.format(self.dest.title(), path))
        setattr(namespace, self.dest, path)


class TestsFileAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self.type = dict
        if nargs is not None:
            raise ValueError('nargs not allowed')
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        path = pathlib.Path(values)
        if not path.exists():
            parser.error('{} \'{}\' does not exist.'.format(self.dest.title(), path))
        if not path.is_file():
            parser.error('{} \'{}\' is not a file.'.format(self.dest.title(), path))
        try:
            tests = dict([ (str(k),v) for k,v in ctxyaml_load(path).items() ])
            setattr(namespace, self.dest, tests)
        except:
            #TODO: give some hints on error in the tests file
            parser.error('{} \'{}\' is not a valid tests specification.'.format(self.dest.title(), path))


def filter_tests(parser, args):
    if hasattr(args, 'tests') and hasattr(args, 'test') and args.test:
        for test_id in args.test:
            if test_id not in args.tests:
                parser.error('Test \'{}\' is not available in tests specification.'.format(test_id))
        tests = dict([ (k,v) for k,v in args.tests.items() if k in args.test ])
        setattr(args, 'tests', tests)


def collect_input_paths(parser, args):
    setattr(args, 'input_paths', dict())
    for id in args.tests.keys():
        args.input_paths[id] = set()
        def collect(a):
            if isinstance(a, pathlib.Path):
                args.input_paths[id].add(str(a))
                if not a.exists():
                    parser.error('Path \'{}\' used in test \'{}\' does not exist.'.format(a, id))
                if not a.is_file():
                    parser.error('Path \'{}\' used in test \'{}\' is not a file.'.format(a, id))
                return get_input_path(a)
            if isinstance(a, list):
                return [ collect(e) for e in a ]
            if isinstance(a, dict):
                return dict( [ (collect(k), collect(v)) for k,v in a.items() ] )
            return a
        args.tests[id] = collect(args.tests[id])
 
def collect_solution_path(parser, args):
    solution = args.solution.resolve()
    for k in args.input_paths.keys():
        args.input_paths[k].add(str(solution))
    args.solution = get_input_path(solution)

def create_checkings(parser, args):
    checkings = dict()
    for id in args.tests.keys():
        checkings[id] = Checking(system=args.system(output_directory = args.result / id, paths=args.input_paths[id]), id=id, test=args.tests[id], solution=args.solution)
    setattr(args, 'checkings', checkings)

def config_parser_update(parser, judge_path=None):
    if judge_path is None:
        parser.add_argument('judge', action=ExistingFileAction, help='Judge script')
    else:
        parser.set_defaults(judge=pathlib.Path(judge_path))
    def execute(args):
        with urllib.request.urlopen(config.DISTRIBUTION_ADDRESS) as library_request:
            if library_request.status == 200 and library_request.reason == 'OK':
                library_data = library_request.read()
                library_path = args.judge.resolve().parent / config.DISTRIBUTION_PATH
                with library_path.open('wb') as library_file:
                    library_file.write(library_data)
                library_path.chmod(0o755)
                logging.warning('Kolejka Judge library updated.')
                #TODO Different warning on no-change
            else:
                logging.error('Failed to update Kolejka Judge library: {} ({}).'.format(library_request.reason, library_request.status))
    parser.set_defaults(execute=execute)

def config_parser_task(parser, judge_path=None):
    if judge_path is None:
        parser.add_argument('judge', action=ExistingFileAction, help='Judge script')
    else:
        parser.set_defaults(judge=pathlib.Path(judge_path))
    parser.add_argument('tests', action=TestsFileAction, help='Tests specification')
    parser.add_argument('--test', action='append', help='Test to run')
    parser.add_argument('solution', action=ExistingFileAction, help='Solution')
    parser.add_argument('task', type=pathlib.Path, help='Output task directory')
    parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite output task directory')
    def execute(args):
        if args.task.exists():
            if args.overwrite:
                if args.task.is_symlink():
                    args.task.unlink()
                else:
                    shutil.rmtree(args.task)
            else:
                parser.error('Task \'{}\' already exists.'.format(args.task))
        filter_tests(parser, args)
        kolejka_task(args.task, args.tests, args.solution, args.judge, debug=args.debug)
    parser.set_defaults(execute=execute)

def config_parser_client(parser, judge_path=None):
    if judge_path is None:
        parser.add_argument('judge', action=ExistingFileAction, help='Judge script')
    else:
        parser.set_defaults(judge=pathlib.Path(judge_path))
    parser.add_argument('tests', action=TestsFileAction, help='Tests specification')
    parser.add_argument('--test', action='append', help='Test to run')
    parser.add_argument('solution', action=ExistingFileAction, help='Solution')
    parser.add_argument('result', type=pathlib.Path, help='Output result directory')
    parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite output result directory')
    def execute(args):
        if args.result.exists():
            if args.overwrite:
                if args.result.is_symlink():
                    args.result.unlink()
                else:
                    shutil.rmtree(args.result)
            else:
                parser.error('Result \'{}\' already exists.'.format(args.result))
        filter_tests(parser, args)
        with tempfile.TemporaryDirectory() as temp_dir:
            kolejka_task(temp_dir, args.tests, args.solution, args.judge, exist_ok=True, debug=args.debug)
            subprocess.run(['kolejka-client', 'execute', temp_dir, args.result], check=True)
            #TODO: maybe, use kolejka.client instead?
    parser.set_defaults(execute=execute)

def known_systems():
    from kolejka.judge.systems import LocalSystem, ObserverSystem
    known_systems = {
        'local': LocalSystem,
        'observer': ObserverSystem,
    }
    return known_systems
def default_system():
    return 'local'

def config_parser_execute(parser, judge_path=None):
    if judge_path is None:
        parser.add_argument('judge', action=ExistingFileAction, help='Judge script')
    else:
        parser.set_defaults(judge=pathlib.Path(judge_path))
    parser.add_argument('tests', action=TestsFileAction, help='Tests specification')
    parser.add_argument('--test', action='append', help='Test to run')
    parser.add_argument('solution', action=ExistingFileAction, help='Solution')
    parser.add_argument('result', type=pathlib.Path, help='Output result directory')
    parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite output result directory')
    parser.add_argument('--results', default='results.yaml', action=RelativePathAction, help='Results filename in output result directory')
    systems = known_systems()
    system = default_system()
    if system not in systems:
        parser.error('Default system \'{}\' is not available.'.format(system))
    for system_id, System in systems.items():
        parser.add_argument('--{}'.format(system_id), dest='system', action='store_const', const=system_id, default=system, help='Use {} execution environment'.format(system_id.title()))

    def initialize(args):
        if args.result.exists():
            if args.overwrite:
                if args.result.is_symlink():
                    args.result.unlink()
                else:
                    shutil.rmtree(args.result)
            else:
                parser.error('Result \'{}\' already exists.'.format(args.result))
        filter_tests(parser, args)
        collect_input_paths(parser, args)
        collect_solution_path(parser, args)
        setattr(args, 'system', systems[args.system])
        create_checkings(parser, args)
    parser.set_defaults(initialize=initialize)

    def finalize(args):
        from kolejka.judge.satori import satori_result
        from kolejka.judge.result import ResultDict
        results = ResultDict()
        for id, checking in args.checkings.items():
            if checking.result is not None:
                results.set(id, checking.result)
                satori_result(checking.test, results[id], args.result / id )
            else:
                r = ResultDict()
                r.set_status('INT')
                r.set('message', 'Checking did not set result.')
                results.set(id, r)
        result_file = args.result / args.results
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_dir = args.result.resolve()
        def path_filter(v):
            if isinstance(v, list):
                return [ e for e in [ path_filter(e) for e in v ] if e is not None ]
            if isinstance(v, dict):
                return dict([ (k,e) for k,e in [ (path_filter(k),path_filter(e)) for k,e in v.items() ] if k is not None and e is not None ])
            if isinstance(v, pathlib.Path):
                try:
                    v.relative_to(result_dir)
                except ValueError:
                    return None
            return v
        ctxyaml_dump(path_filter(results.yaml), result_file)
    parser.set_defaults(finalize=finalize)
    
    def execute(args):
        args.initialize(args)
        from importlib.util import module_from_spec
        from importlib.machinery import SourceFileLoader, ModuleSpec
        spec = ModuleSpec('judge', SourceFileLoader('judge', str(args.judge.resolve())))
        judge = module_from_spec(spec)
        spec.loader.exec_module(judge)
        for checking in args.checkings.values():
            judge.judge(checking)
        args.finalize(args)
    parser.set_defaults(execute=execute)


def config_parser(parser, judge_path=None):
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    subparser = subparsers.add_parser('update')
    config_parser_update(subparser, judge_path=judge_path)
    subparser = subparsers.add_parser('task')
    config_parser_task(subparser, judge_path=judge_path)
    subparser = subparsers.add_parser('client')
    config_parser_client(subparser, judge_path=judge_path)
    subparser = subparsers.add_parser('execute')
    config_parser_execute(subparser, judge_path=judge_path)

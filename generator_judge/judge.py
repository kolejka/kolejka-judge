import pathlib
DEFAULT_TESTS_FILE='tests/tests.yaml'
DEFAULT_SOLUTION_GLOB='solution/*'
DEFAULT_ENVIRONMENT='local'
DEFAULT_JUDGE_DESCRIPTION='SATORI KOLEJKA judge'

CHECKING_DIR=pathlib.Path('CHECKING')
TOOLS_DIR=CHECKING_DIR/'tools'
LOGS_DIR=CHECKING_DIR/'logs'

def reset_dirs():
    import shutil
    shutil.rmtree(CHECKING_DIR)
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def known_environments():
    from kolejka.judge.environments import LocalComputer, KolejkaObserver
    known_environments = {
        'local': LocalComputer,
        'observer': KolejkaObserver,
        #'kolejka' : KolejkaTask,
    }
    return known_environments

def argument_parser(description=DEFAULT_JUDGE_DESCRIPTION):
    import argparse
    import glob
    import pathlib
    parser = argparse.ArgumentParser(description=description)
    envs = known_environments()
    for env_id, env_cls in envs.items():
        parser.add_argument(
            '--{}'.format(env_id),
            dest='environment',
            action='store_const',
            const=env_id,
            default=DEFAULT_ENVIRONMENT,
        )
    if pathlib.Path(DEFAULT_TESTS_FILE).is_file():
        parser.add_argument('--tests', default='tests/tests.yaml', type=str, help='Tests description')
    else:
        parser.add_argument('--tests', required=True, type=str, help='Tests description')
    parser.add_argument('--test', type=str, help='Test to run')
    solution = list(glob.glob(DEFAULT_SOLUTION_GLOB))
    if len(solution) == 1:
        parser.add_argument('--solution', default=solution[0], type=str, help='Solution file')
    else:
        parser.add_argument('--solution', required=True, type=str, help='Solution file')
    parser.add_argument('--output-dir', default='results', type=str, help='Output directory')
    parser.add_argument('--results', default='results/results.yaml', type=str, help='Results file')
    return parser

def parse_args(args=None, namespace=None, description=DEFAULT_JUDGE_DESCRIPTION):
    import argparse
    import pathlib
    envs = known_environments()
    parser = argument_parser(description=description)
    args = parser.parse_args(args=args, namespace=namespace)

    if not pathlib.Path(args.tests).is_file():
        parser.error('TESTS file {} does not exist'.format(args.tests))

    try:
        import ctxyaml
        with open(args.tests) as tests_file:
            tests = ctxyaml.load(tests_file)
    except:
        parser.error('Failed to load TESTS file {}'.format(args.tests))

    try:
        if args.test is not None:
            tests = {
                args.test : tests[args.test]
            }
    except:
        parser.error('TEST {} does not exist in TESTS file {}'.format(args.test, args.tests))
    
    if not pathlib.Path(args.solution).is_file():
        parser.error('SOLUTION file {} does not exist'.format(args.solution))

    if not args.environment in envs:
        parser.error('Execution environment {} does not exist'.format(args.environment))

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    if not pathlib.Path(args.output_dir).is_dir():
        parser.error('Output directory {} is not a directory'.format(args.output_dir))

    solution = pathlib.Path(args.solution)
    results = pathlib.Path(args.results)
    environment = envs[args.environment]
    output_dir = pathlib.Path(args.output_dir)

    return argparse.Namespace(tests=tests, solution=solution, results=results, environment=environment, output_dir=output_dir)

def write_results(args, results):
    args.results.parent.mkdir(parents=True, exist_ok=True)
    import ctxyaml
    with args.results.open('w') as results_file:
        ctxyaml.dump(results, results_file)

DEFAULT_GROUPS = [
        'satori-judge',
    ]
DEFAULT_USERS = [
    {
        'user' : 'satori-judge-test',
        'home' : 'home/satori-judge-test',
        'groups' : ['satori-judge'],
    },
    {
        'user' : 'satori-judge-tool',
        'home' : 'home/satori-judge-tool',
        'groups' : ['satori-judge'],
    },
    {
        'user' : 'satori-judge-solution',
        'home' : 'home/satori-judge-solution',
        'groups' : ['satori-judge'],
    },
    {
        'user' : 'satori-judge-run',
        'home' : 'home/satori-judge-run',
    },
    ]
DEFAULT_DIRECTORIES = [
    {
        'path' : 'test',
        'user':'satori-judge-test',
        'group':'satori-judge-test',
        'mode':0o750,
    },
    {
        'path' : 'solution',
        'user':'satori-judge-test',
        'group':'satori-judge',
        'mode':0o750,
    },
    {
        'path' : 'solution/src',
        'user':'satori-judge-test',
        'group':'satori-judge',
        'mode':0o750,
    },
    {
        'path' : 'solution/build',
        'user':'satori-judge-solution',
        'group':'satori-judge',
        'mode':0o750,
    },
    {
        'path' : 'tool',
        'user':'satori-judge-tool',
        'group':'satori-judge-tool',
        'mode':0o750,
    },
    {
        'path' : 'tool/src',
        'user':'satori-judge-tool',
        'group':'satori-judge-tool',
        'mode':0o750,
    },
    {
        'path' : 'tool/build',
        'user':'satori-judge-tool',
        'group':'satori-judge-tool',
        'mode':0o750,
    },
    ]

from collections import OrderedDict
from copy import deepcopy
import glob
import grp
import itertools
import os
from pathlib import Path
import pwd
from typing import Optional, Tuple

from kolejka.judge.commands.base import CommandBase
from kolejka.judge.tasks.base import Task
from kolejka.judge.environments import ExecutionEnvironment
from kolejka.judge.validators import ProgramExistsPrerequisite, FileExistsPrerequisite, ExitCodePostcondition

class RunCommand(CommandBase):
    def __init__(self, executable, cmdline_options=None, stdin=None, stdout=None, stderr=None, **kwargs):
        super().__init__(**kwargs)
        self.executable = Path(executable)
        assert self.executable.is_absolute()
        self.cmdline_options = cmdline_options or []
        if stdin is not None:
            self.stdin = Path(stdin)
            assert self.stdin.is_absolute()
        else:
            self.stdin = Path('/dev/null')
        if stdout is not None:
            self.stdout = Path(stdout)
            assert self.stdout.is_absolute()
        else:
            self.stdout = None
        if stderr is not None:
            self.stderr = Path(stderr)
            assert self.stderr.is_absolute()
        else:
            self.stderr = None

    def get_stdin_file(self):
        return self.stdin

    def get_stdout_file(self):
        return self.stdout or super().get_stdout_file()

    def get_stderr_file(self):
        return self.stderr or super().get_stderr_file()

    def get_command(self):
        return [self.executable] + self.cmdline_options

    def prerequisites(self):
        prerequisites = [ProgramExistsPrerequisite(self.executable)]
        if self.stdin is not None:
            prerequisites.append(FileExistsPrerequisite(self.stdin))
        return prerequisites

class DiffCommand(CommandBase):
    def __init__(self, file1, file2, **kwargs):
        super().__init__(**kwargs)
        self.file1 = Path(file1)
        assert self.file1.is_absolute()
        self.file2 = Path(file2)
        assert self.file2.is_absolute()

    def get_command(self):
        return [ 'diff', '-q', '-w', '-B', self.file1, self.file2 ]

    def prerequisites(self):
        return [
            FileExistsPrerequisite(self.file1),
            FileExistsPrerequisite(self.file2),
        ]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'ANS')
        ]


class SystemCommand(CommandBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    @staticmethod
    def get_superuser():
        #TODO: Maybe we should move this decission somewhere else? To the environment?
        return os.getuid() == 0

class GroupAddCommand(SystemCommand):
    def __init__(self, group, gid=None, **kwargs):
        super().__init__(**kwargs)
        self.group = group
        self.gid = gid
    def get_command(self):
        if not self.get_superuser():
            return [ 'true' ]
        comm = []
        comm += [ 'groupadd' ]
        if self.gid is not None:
            comm += [ '--gid', str(self.gid) ]
        comm += [ self.group ]
        return comm

class UserAddCommand(SystemCommand):
    def __init__(self, user, uid=None, home=None, groups=None, shell=None, comment=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.uid = uid
        if home is not None:
            self.home = Path(home)
            assert self.home.is_absolute()
        else:
            self.home = home
        self.groups = groups
        self.shell = shell
        self.comment = comment or user
    def get_command(self):
        if not self.get_superuser():
            return [ 'true' ]
        comm = []
        comm += [ 'useradd', '--comment', self.comment ]
        if self.uid is not None:
            comm += [ '--uid', str(self.uid) ]
        if self.home is not None:
            comm += [ '--create-home', '--home-dir', str(self.home) ]
        else:
            comm += [ '--no-create-home' ]
        if self.shell is not None:
            comm += [ '--shell', str(self.shell) ]
        if self.groups is not None:
            comm += [ '--groups', ','.join([ str(group) for group in self.groups]) ]
        comm += [ '--user-group', self.user ]
        return comm

class DirectoryAddCommand(SystemCommand):
    def __init__(self, path, user=None, group=None, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.path = Path(path)
        assert self.path.is_absolute()
        self.user = user
        self.group = group
        self.mode = mode
    def get_octal_mode(self):
        if self.mode is None:
            return None
        if isinstance(self.mode, int):
            return '0'+oct(self.mode)[2:]
        return str(self.mode)
    def get_command(self):
        comm = []
        comm += [ 'install' ]
        if self.user is not None and self.get_superuser():
            comm += [ '--owner', str(self.user) ]
        if self.group is not None and self.get_superuser():
            comm += [ '--group', str(self.group) ]
        if self.mode is not None:
            comm += [ '--mode', self.get_octal_mode() ]
        comm += [ '--directory', str(self.path) ]
        return comm

class InstallCommand(SystemCommand):
    def __init__(self, source, destination, user=None, group=None, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.source = Path(source)
        assert self.source.is_absolute()
        self.destination = Path(destination)
        assert self.destination.is_absolute()
        self.user = user
        self.group = group
        self.mode = mode
    def get_octal_mode(self):
        if self.mode is None:
            return None
        if isinstance(self.mode, int):
            return '0'+oct(self.mode)[2:]
        return str(self.mode)
    def get_command(self):
        comm = []
        comm += [ 'install' ]
        if self.user is not None and self.get_superuser():
            comm += [ '--owner', str(self.user) ]
        if self.group is not None and self.get_superuser():
            comm += [ '--group', str(self.group) ]
        if self.mode is not None:
            comm += [ '--mode', self.get_octal_mode() ]
        comm += [ '--no-target-directory', str(self.source), str(self.destination) ]
        return comm

class SatoriSystemPrepareTask(Task):
    def __init__(self, add_users = DEFAULT_USERS, add_groups = DEFAULT_GROUPS, add_directories = DEFAULT_DIRECTORIES, **kwargs):
        super().__init__()
        self.groups = OrderedDict()
        self.users = OrderedDict()
        self.directories = OrderedDict()
        for group in (add_groups or []):
            self.add_group(group)
        for user in (add_users or []):
            self.add_user(user)
        for directory in (add_directories or []):
            self.add_directory(directory)

    def add_group(self, group, **kwargs):
        if isinstance(group, dict):
            kwargs.update(group)
            group=kwargs['group']
        group=str(group).strip()
        kwargs['group'] = group
        if group not in self.groups and group not in self.users:
            self.groups[group] = kwargs

    def add_user(self, user, **kwargs):
        if isinstance(user, dict):
            kwargs.update(user)
            user=kwargs['user']
        user=str(user).strip()
        kwargs['user'] = user
        if 'home' in kwargs and kwargs['home'] is not None:
            home_path = Path(kwargs['home'])
            assert not home_path.is_absolute()
        if user not in self.users:
            self.users[user] = kwargs
            if kwargs.get('groups', None) is not None:
                for group in kwargs['groups']:
                    self.add_group(group)
            if user in self.groups:
                del self.groups[user]

    def add_directory(self, path, **kwargs):
        if isinstance(path, dict):
            kwargs.update(path)
            path=kwargs['path']
        path=Path(path)
        assert not path.is_absolute()
        kwargs['path'] = path
        if path not in self.directories:
            self.directories[path] = kwargs
            if kwargs.get('user', None) is not None:
                self.add_user(kwargs['user'])
            if kwargs.get('group', None) is not None:
                self.add_group(kwargs['group'])

    def execute(self, name, environment: ExecutionEnvironment) -> Tuple[Optional[str], Optional[object]]:
        for group in self.groups.values():
            add_group = GroupAddCommand(**group)
            try:
                grp.getgrnam(add_group.group)
            except:
                environment.run_command_step(add_group, name='{}_groupadd_{}'.format(name, add_group.group))
        for user in self.users.values():
            if 'home' in user and user['home'] is not None:
                user['home'] = environment.get_path(user['home']).resolve()
            add_user = UserAddCommand(**user)
            try:
                pwd.getpwnam(add_user.user)
            except:
                environment.run_command_step(add_user, name='{}_useradd_{}'.format(name, add_user.user))
        for directory in self.directories.values():
            directory['path'] = environment.get_path(directory['path']).resolve()
            add_directory = DirectoryAddCommand(**directory)
            environment.run_command_step(add_directory, name='{}_directoryadd_{}'.format(name, str(add_directory.path).replace('/','_')))
        return None, None

class SatoriSourcePrepareTask(Task):
    def __init__(self, source, destination, basename, override=None, user=None, group=None, mode=None, **kwargs):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        assert not self.destination.is_absolute()
        self.basename = basename
        if override is not None:
            self.override = Path(override)
        else:
            self.override = None
        self.user = user
        self.group = group
        self.mode = mode

    def execute(self, name, environment: ExecutionEnvironment) -> Tuple[Optional[str], Optional[object]]:
        environment.run_command_step(DirectoryAddCommand(path=environment.get_path(self.destination).resolve(), user=self.user, group=self.group, mode=0o750), name='{}_source_dir'.format(name))

        source_command = InstallCommand(environment.get_path(self.source).resolve(), (environment.get_path(self.destination)/(self.basename+'.cpp')).resolve(), user=self.user, group=self.group, mode=self.mode)
        #TODO: Add other languages
        #TODO: Add zip extraction
        #TODO: Add java folders structure
        environment.run_command_step(source_command, name='{}_source'.format(name))
        if self.override:
            #TODO: Add override handling
            pass

        return None, None

class CompileCPPCommand(CommandBase):
    def __init__(self, source_dir, build_dir, **kwargs):
        super().__init__(**kwargs)
        self.source_dir = Path(source_dir)
        assert self.source_dir.is_absolute()
        self.build_dir = Path(build_dir)
        assert self.build_dir.is_absolute()
    def find_source(self):
        return list(glob.iglob(str(self.source_dir)+'/*.cpp'))
    def applicable(self):
        return len(self.find_source()) > 0
    def get_command(self):
        comm = []
        comm += [ 'g++', '-Wall', '-O2', ]
        comm += [ '-o', str(self.build_dir/'a.out') ] + self.find_source()
        return comm
    def get_executable_script(self):
        return '#!/bin/sh\nexec {}\n'.format(self.build_dir/'a.out')
        
class SatoriBuildTask(Task):
    def __init__(self, source_dir, build_dir, executable_script, basename=None, user=None, group=None, **kwargs):
        super().__init__()
        self.source_dir = Path(source_dir)
        assert not self.source_dir.is_absolute()
        self.build_dir = Path(build_dir)
        assert not self.build_dir.is_absolute()
        self.executable_script = Path(executable_script)
        assert not self.executable_script.is_absolute()
        self.basename = basename
        self.user = user
        self.group = group

    def execute(self, name, environment: ExecutionEnvironment) -> Tuple[Optional[str], Optional[object]]:
        environment.run_command_step(DirectoryAddCommand(path=environment.get_path(self.build_dir).resolve(), user=self.user, group=self.group, mode=0o750), name='{}_source_dir'.format(name))

        call_script = '#!/bin/sh\nexec true\n'
        build_commands = list()
        cpp = CompileCPPCommand(environment.get_path(self.source_dir).resolve(), environment.get_path(self.build_dir).resolve())
        if cpp.applicable():
            build_commands.append(cpp)
            call_script = cpp.get_executable_script()
        #TODO: Add cmake
        #TODO: Add make
        #TODO: Add other languages


        for num, command in zip(range(1,len(build_commands)+1), build_commands):
            environment.run_command_step(command, name='{}_{}'.format(name, num))
        with environment.get_path(self.executable_script).open('w') as script:
            script.write(call_script)
        environment.get_path(self.executable_script).chmod(0o750)
        return None, None

class SatoriRunTask(Task):
    def __init__(self, executable, cmdline_options = None, stdin=None, stdout=None, stderr=None):
        super().__init__()
        self.executable = Path(executable)
        assert not self.executable.is_absolute()
        self.cmdline_options = cmdline_options or []
        if stdin is not None:
            self.stdin = Path(stdin)
        else:
            self.stdin = None
        if stdout is not None:
            self.stdout = Path(stdout)
            assert not self.stdout.is_absolute()
        else:
            self.stdout = None
        if stderr is not None:
            self.stderr = Path(stderr)
            assert not self.stderr.is_absolute()
        else:
            self.stderr = None

    def execute(self, name, environment: ExecutionEnvironment) -> Tuple[Optional[str], Optional[object]]:
        environment.run_command_step(RunCommand(executable=environment.get_path(self.executable).resolve(), cmdline_options=self.cmdline_options, stdin=self.stdin and environment.get_path(self.stdin).resolve(), stdout=self.stdout and environment.get_path(self.stdout).resolve(), stderr=self.stderr and environment.get_path(self.stderr).resolve()), name='{}_source_dir'.format(name))
        return None, None

class SatoriDiff(Task):
    def __init__(self, file1, file2):
        super().__init__()
        self.file1 = Path(file1)
        self.file2 = Path(file2)
    def execute(self, name, environment: ExecutionEnvironment) -> Tuple[Optional[str], Optional[object]]:
        environment.run_command_step(DiffCommand(file1=environment.get_path(self.file1).resolve(), file2=environment.get_path(self.file2).resolve()), name='{}_source_dir'.format(name))
        return None, None

class SatoriSolutionPrepareTask(SatoriSourcePrepareTask):
    def __init__(self, source, destination=Path('solution/src'), basename='solution', override=None, user='satori-judge-test', group='satori-judge', mode=0o750, **kwargs):
        super().__init__(source=source, destination=destination, basename=basename, override=override, user=user, group=group, mode=mode, **kwargs)

class SatoriSolutionBuildTask(SatoriBuildTask):
    def __init__(self, source_dir=Path('solution/src'), build_dir=Path('solution/build'), executable_script='solution/solution', user='satori-judge-solution', group='satori-judge-solution', **kwargs):
        super().__init__(source_dir=source_dir, build_dir=build_dir, executable_script=executable_script, user=user, group=group, **kwargs)

class SatoriSolutionRunTask(SatoriRunTask):
    def __init__(self, executable=Path('solution/solution'), user='satori-judge-run', group='satori-judge-run', stdin='test/input', stdout='test/output', **kwargs):
        super().__init__(executable=executable, stdin=stdin, stdout=stdout, **kwargs)

class SatoriToolPrepareTask(SatoriSourcePrepareTask):
    def __init__(self, tool_name, source, destination=Path('tool/src'), override=None, user='satori-judge-tool', group='satori-judge-tool', mode=0o750, **kwargs):
        super().__init__(source=source, destination=destination/tool_name, basename=tool_name, override=override, user=user, group=group, mode=mode, **kwargs)

class SatoriToolBuildTask(SatoriBuildTask):
    def __init__(self, tool_name, source_dir=Path('tool/src'), build_dir=Path('tool/build'), executable_dir=Path('tool'), user='satori-judge-tool', group='satori-judge-tool', **kwargs):
        super().__init__(source_dir=source_dir/tool_name, build_dir=build_dir/tool_name, executable_script=executable_dir/tool_name, user=user, group=group, **kwargs)

class SatoriToolRunTask(SatoriRunTask):
    def __init__(self, tool_name, executable_dir=Path('tool'), user='satori-judge-tool', group='satori-judge-tool', **kwargs):
        super().__init__(executable=executable_dir/tool_name, **kwargs)

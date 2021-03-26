# vim:ts=4:sts=4:sw=4:expandtab

import copy
import csv
import json
import os
import pathlib
import re
import shlex
import shutil
import time

from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import *
from kolejka.judge.tasks.build import *
from kolejka.judge.tasks.check import *
from kolejka.judge.tasks.rules import *
from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.system import *
from kolejka.judge.tasks.tools import *


__all__ = [ 'PostgresPrepareTask', 'PostgresResetTask', 'BuildPostgresTask', 'SolutionBuildPostgresTask', 'ToolBuildPostgresTask', 'ToolPostgresTask', 'GeneratorPostgresTask', 'HinterPostgresTask', 'CheckerPostgresTask', 'SingleBuildIOPostgresTask', 'MultipleBuildIOPostgresTask' ]
def __dir__():
    return __all__

LOG_FIELDS = [ 'log_time', 'user_name', 'database_name', 'process_id', 'connection_from', 'session_id', 'session_line_num', 'command_tag', 'session_start_time', 'virtual_transaction_id', 'transaction_id', 'error_severity', 'sql_state_code', 'message', 'detail', 'hint', 'internal_query', 'internal_query_pos', 'context', 'query', 'query_pos', 'location', 'application_name', 'backend_type' ]
def collect_logs(log_directory, application_name=None):
    logs = list()
    for log_path in sorted(pathlib.Path(log_directory).glob('*.csv')):
        with open(log_path, newline='') as log_file:
            for row in csv.reader(log_file):
                logs.append(dict(zip(LOG_FIELDS[:len(row)], row[:len(LOG_FIELDS)])))
    if application_name is not None:
        connections = set()
        for log in logs:
            m = re.match(r'^connection authorized:.*application_name=([^: ]+).*$', log['message'], flags=re.MULTILINE|re.IGNORECASE|re.DOTALL)
            if m and m[1] == application_name:
                connections.add(log['process_id'])
        logs = [ log for log in logs if log['process_id'] in connections ]
    return logs
def collect_auto_explain(log_directory, application_name=None):
    logs = collect_logs(log_directory, application_name)
    durations = list()
    costs = list()
    startups = list()
    times = list()
    for log in logs:
        m = re.match(r'^duration:([^:]+) plan:(.+)$', log['message'], flags=re.MULTILINE|re.IGNORECASE|re.DOTALL)
        if m:
            duration = float(m[1].strip().split(' ')[0])
            durations.append(duration)
            try:
                j = json.loads(m[2])
                startup = j.get('Plan', {}).get('Startup Cost', 0.0)
                cost = j.get('Plan', {}).get('Total Cost', 0.0)
                time = j.get('Plan', {}).get('Actual Total Time', 0.0)
            except:
                pass
            startups.append(startup)
            costs.append(cost)
            times.append(time)
    return {
        'statements' : len(durations),
        'durations' : round(sum(durations), 4),
        'startup_costs' : round(sum(startups), 4),
        'costs' : round(sum(costs), 4),
        'times' : round(sum(times), 4),
    }


class PostgresTask(TaskBase):
    DEFAULT_VERSION=config.POSTGRES_VERSION
    DEFAULT_DATA_DIR=config.POSTGRES_DATA_DIR
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_LOCALE=config.POSTGRES_LOCALE
    DEFAULT_DB=config.POSTGRES_DB
    DEFAULT_DB_ADMIN=config.POSTGRES_DB_ADMIN
    DEFAULT_DB_USER=config.POSTGRES_DB_USER
    @default_kwargs
    def __init__(self, version, data_dir, socket_dir, locale, db, db_admin, db_user, **kwargs):
        super().__init__(**kwargs)
        self.version = version
        self.data_dir = get_output_path(data_dir)
        self.socket_dir = get_output_path(socket_dir)
        self.locale = locale
        self.db = db
        self.db_admin = db_admin
        self.db_user = db_user


class PostgresPrepareTask(PostgresTask):
    DEFAULT_RESULT_ON_ERROR='INT'
    DEFAULT_INIT_COMMANDS=[]
    DEFAULT_INIT_FILES=[]
    @default_kwargs
    def __init__(self, init_commands, init_files, users =config.POSTGRES_USERS, groups =config.POSTGRES_GROUPS, directories =config.POSTGRES_DIRECTORIES, **kwargs):
        super().__init__(**kwargs)
        self.prepare_task = SystemPrepareTask(users=users, groups=groups, directories=directories, **kwargs)
        self.init_commands = init_commands
        self.init_files = init_files

    def set_system(self, system):
        super().set_system(system)
        self.prepare_task.set_system(system)

    def set_name(self, name):
        super().set_name(name)
        self.prepare_task.set_name(name+'_prepare')

    def execute(self):
        prepare_result = self.prepare_task.execute()
        if prepare_result.status:
            self.set_result(prepare_result.status, 'prepare', prepare_result)
        else:
            self.run_command('initdb', PInitDBCommand, version=self.version, data_dir=self.data_dir, locale=self.locale, db_admin=self.db_admin)
            with self.resolve_path(self.data_dir/'pg_hba.conf').open('w') as hba_file:
                hba_file.write('local all %s peer map=default\n' % (self.db_admin,))
                hba_file.write('local all %s peer map=default\n' % (self.db_user,))
            with self.resolve_path(self.data_dir/'pg_ident.conf').open('w') as ident_file:
                ident_file.write('default root %s\n' % (self.db_admin,))
                ident_file.write('default root %s\n' % (self.db_user,))
                if not self.system.superuser:
                    ident_file.write('default %s %s\n' % (self.system.current_user, self.db_admin))
                    ident_file.write('default %s %s\n' % (self.system.current_user, self.db_user))
                ident_file.write('default %s %s\n' % (config.USER_POSTGRES, self.db_admin))
                ident_file.write('default %s %s\n' % (config.USER_POSTGRES, self.db_user))
                ident_file.write('default %s %s\n' % (config.USER_TEST, self.db_admin))
                ident_file.write('default %s %s\n' % (config.USER_TEST, self.db_user))
                ident_file.write('default %s %s\n' % (config.USER_BUILD, self.db_user))
                ident_file.write('default %s %s\n' % (config.USER_EXEC, self.db_user))
            self.run_command('postgres', PostgresCommand, version=self.version, data_dir=self.data_dir, socket_dir=self.socket_dir)
            with self.resolve_path(self.data_dir/'pg_start.sh').open('w') as start_file:
                start_file.write('#!/bin/sh\n')
                start_file.write('exec '+ ' '.join([ shlex.quote(self.system.resolve(a)) for a in self.commands['postgres'].command ]) + ' "$@"\n')
            self.resolve_path(self.data_dir/'pg_start.sh').chmod(0o755)
            time.sleep(0.5)
            self.run_command('createuser', PCreateUserCommand, version=self.version, socket_dir=self.socket_dir, db_admin=self.db_admin, db_user=self.db_user)
            self.run_command('createdb', PCreateDBCommand, version=self.version, socket_dir=self.socket_dir, db_admin=self.db_admin, db_user=self.db_user, db=self.db)
            if self.init_commands or self.init_files:
                self.run_command('init', PSQLAdminCommand, version=self.version, socket_dir=self.socket_dir, db=self.db, db_user=self.db_admin, files=self.init_files, commands=self.init_commands)
        return self.result

class PostgresResetTask(PostgresTask):
    DEFAULT_RESULT_ON_ERROR='INT'
    DEFAULT_INIT_COMMANDS=[]
    DEFAULT_INIT_FILES=[]
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, init_commands, init_files, **kwargs):
        super().__init__(**kwargs)
        self.init_commands = init_commands
        self.init_files = init_files

    def execute(self):
        self.run_command('dropdb', PDropDBCommand, version=self.version, socket_dir=self.socket_dir, db_admin=self.db_admin, db=self.db)
        self.run_command('createdb', PCreateDBCommand, version=self.version, socket_dir=self.socket_dir, db_admin=self.db_admin, db_user=self.db_user, db=self.db)
        if self.init_commands or self.init_files:
            self.run_command('init', PSQLAdminCommand, version=self.version, socket_dir=self.socket_dir, db=self.db, db_user=self.db_admin, files=self.init_files, commands=self.init_commands)
        return self.result


class BuildPostgresTask(PostgresTask, BuildTask):
    DEFAULT_QUIET=True
    DEFAULT_TUPLES_ONLY=False
    DEFAULT_ALIGN=True
    DEFAULT_IGNORE_ERRORS=False
    DEFAULT_APPLICATION_NAME='psql'
    @default_kwargs
    def __init__(self, task=None, quiet=None, tuples_only=None, align=None, ignore_errors=None, application_name=None, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.sql_script = self.build_directory / 'exec.sql'
        self.quiet = quiet
        self.tuples_only = tuples_only
        self.align = align
        self.ignore_errors = ignore_errors
        self.application_name = application_name

    def get_source_file(self):
        sqls = []
        tasks = []
        for f in self.find_files(self.source_directory):
            if self.task:
                if f.match(self.task+'.[Ss][Qq][Ll]'):
                    tasks += [f]
            if f.match('*.[Ss][Qq][Ll]'):
                sqls += [f]
        if len(tasks) > 1:
            return None
        if len(tasks) == 1:
            return tasks[0]
        if len(sqls) == 1:
            return sqls[0]
        return None

    def ok(self):
        return self.get_source_file() is not None

    def get_execution_command(self):
        psql = PSQLCommand(files=[self.sql_script], version=self.version, socket_dir=self.socket_dir, db=self.db, db_user=self.db_user, quiet=self.quiet, tuples_only=self.tuples_only, align=self.align, ignore_errors=self.ignore_errors, application_name=self.application_name)
        return psql.command

    def execute_build(self):
        with self.resolve_path(self.get_source_file()).open() as source_file:
            sql_script_body = source_file.read()
            if self.task:
                new_body = []
                active = False
                starter = re.compile(r'\s*--\s*'+re.escape(self.task)+'\s*', flags=re.IGNORECASE)
                stoper = re.compile(r'\s*----\s*')
                for line in sql_script_body.splitlines(keepends=True):
                    if not active and starter.fullmatch(line):
                        active = True
                    if active:
                        new_body.append(line)
                    if active and stoper.fullmatch(line):
                        active = False
                if new_body:
                    sql_script_body = ''.join(new_body)
            exec_path = self.resolve_path(self.sql_script)
            with exec_path.open('w') as exec_file:
                exec_file.write(sql_script_body)
            if self.system.superuser:
                shutil.chown(exec_path, self.user, self.group)
            exec_path.chmod(0o644)

class SolutionBuildPostgresTask(SolutionBuildMixin, BuildPostgresTask):
    DEFAULT_EXPLAIN=True
    pass
class ToolBuildPostgresTask(ToolBuildMixin, BuildPostgresTask):
    pass

class ToolPostgresTask(ToolTask):
    DEFAULT_BUILD_TASK=ToolBuildPostgresTask
    @default_kwargs
    def __init__(self, task=None, version=None, socket_dir=None, db=None, db_admin=None, db_user=None, quiet=None, tuples_only=None, align=None, ignore_errors=None, **kwargs):
        self.task = task and str(task)
        self.version = version
        self.socket_dir = socket_dir
        self.db = db
        self.db_admin = db_admin
        self.db_user = db_user
        self.quiet = quiet
        self.tuples_only = tuples_only
        self.align = align
        self.ignore_errors = ignore_errors
        super().__init__(**kwargs)

    def get_tool_name(self):
        tool_name = super().get_tool_name()
        if self.task:
            tool_name += '_' + self.task
        return tool_name

    def get_build_kwargs(self):
        kwargs = super().get_build_kwargs()
        if self.task is not None:
            kwargs['task'] = self.task
        if self.version is not None:
            kwargs['version'] = self.version
        if self.socket_dir is not None:
            kwargs['socket_dir'] = self.socket_dir
        if self.db is not None:
            kwargs['db'] = self.db
        if self.db_admin is not None:
            kwargs['db_admin'] = self.db_admin
        if self.db_user is not None:
            kwargs['db_user'] = self.db_user
        if self.quiet is not None:
            kwargs['quiet'] = self.quiet
        if self.tuples_only is not None:
            kwargs['tuples_only'] = self.tuples_only
        if self.align is not None:
            kwargs['align'] = self.align
        if self.ignore_errors is not None:
            kwargs['ignore_errors'] = self.ignore_errors
        return kwargs


class GeneratorPostgresTask(ToolPostgresTask):
    DEFAULT_TOOL_NAME='generator'
    DEFAULT_OUTPUT_PATH=config.TEST_INPUT
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class HinterPostgresTask(ToolPostgresTask):
    DEFAULT_TOOL_NAME='hinter'
    DEFAULT_OUTPUT_PATH=config.TEST_HINT
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CheckerPostgresTask(ToolPostgresTask):
    DEFAULT_TOOL_NAME='checker'
    DEFAULT_RESULT_ON_ERROR='ANS'
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BuildIOPostgresTask(TaskBase):
    DEFAULT_SOLUTION_SOURCE=config.SOLUTION_SOURCE
    DEFAULT_SOLUTION_BUILD=config.SOLUTION_BUILD
    DEFAULT_SOLUTION_EXEC=config.SOLUTION_EXEC
    DEFAULT_ANSWER_PATH=config.TEST_ANSWER
    DEFAULT_HINTER_OUTPUT_PATH=config.TEST_HINT
    DEFAULT_IGNORE_ERRORS=False
    DEFAULT_TUPLES_ONLY=False
    DEFAULT_ALIGN=True
    DEFAULT_CASE_SENSITIVE=True
    DEFAULT_SPACE_SENSITIVE=False
    DEFAULT_ROW_SORT=False
    DEFAULT_COLUMN_SORT=False
    DEFAULT_CHECKER_IGNORE_ERRORS=False
    DEFAULT_DATA_DIR=config.POSTGRES_DATA_DIR
    DEFAULT_COLLECT_LOGS=True
    DEFAULT_APPLICATION_NAME='kolejkasolution'
    @default_kwargs
    def __init__(self, solution_source, solution_build, solution_exec, answer_path, hinter_output_path, ignore_errors, tuples_only, align, case_sensitive, space_sensitive, row_sort, column_sort, checker_ignore_errors, data_dir, collect_logs, application_name, task=None, max_size=None, regex_count=None, hint_path=None, tool_time=None, generator_source=None, hinter_source=None, checker_source=None, limit_cores=1, limit_time=None, limit_cpu_time=None, limit_real_time=None, limit_memory=None, **kwargs):
        super().__init__(**kwargs)
        self.solution_source = solution_source
        self.solution_build = solution_build
        self.solution_exec = solution_exec
        self.answer_path = answer_path
        self.hint_path = hint_path
        self.tool_time = tool_time
        self.generator_source = generator_source
        self.hinter_source = hinter_source
        self.hinter_output_path = hinter_output_path
        self.ignore_errors = ignore_errors
        self.checker_source = checker_source
        self.checker_ignore_errors = checker_ignore_errors
        self.data_dir = get_output_path(data_dir)
        self.collect_logs = collect_logs
        self.application_name = application_name
        self.limit_cores = limit_cores
        self.limit_cpu_time = limit_time
        self.limit_real_time = None
        if limit_time is not None:
            self.limit_real_time = parse_time(limit_time) + parse_time('1s')
        if limit_cpu_time is not None:
            self.limit_cpu_time = limit_cpu_time
        if limit_real_time is not None:
            self.limit_real_time = limit_real_time
        self.limit_memory = limit_memory
        self.task = task
        self.max_size = max_size
        self.regex_count = regex_count
        self.tuples_only = tuples_only
        self.align = align
        self.case_sensitive = case_sensitive
        self.space_sensitive = space_sensitive
        self.row_sort = row_sort
        self.column_sort = column_sort
        self.init_kwargs = kwargs


class SingleBuildIOPostgresTask(BuildIOPostgresTask):
    DEFAULT_SCORE=1.0
    DEFAULT_APPLICATION_NAME='kolejkasolution'
    @default_kwargs
    def __init__(self, score, **kwargs):
        super().__init__(**kwargs)
        self.score = score

        self.steps = []
        builder = SolutionBuildPostgresTask(source_directory=self.solution_source, build_directory=self.solution_build, execution_script=self.solution_exec, task=self.task, tuples_only=self.tuples_only, align=self.align, ignore_errors=self.ignore_errors, application_name=self.application_name) #TODO:version,...
        self.steps.append(('builder', builder))
        if self.regex_count or self.max_size:
            self.steps.append(('rules', SolutionBuildRulesTask(regex_count=self.regex_count, max_size=self.max_size)))

        hint_path = self.hint_path
        answer_path = None
        if self.generator_source:
            generator = GeneratorPostgresTask(task=self.task, source=self.generator_source, limit_real_time=self.tool_time) #TODO:version,...
            self.steps.append(('generator', generator))
        executor = SolutionExecutableTask(executable=self.solution_exec, answer_path=self.answer_path, limit_cores=self.limit_cores, limit_cpu_time=self.limit_cpu_time, limit_real_time=self.limit_real_time, limit_memory=self.limit_memory)
        answer_path = executor.answer_path
        self.steps.append(('executor', executor))
        if not hint_path and self.hinter_source:
            self.steps.append(('hinterreset', PostgresResetTask())) #TODO:version,...
            if self.generator_source:
                self.steps.append(('hintgenerator', GeneratorPostgresTask(task=self.task, source=self.generator_source, limit_real_time=self.tool_time))) #TODO:version,...
            hinter_time=self.tool_time
            if hinter_time and self.limit_real_time and hinter_time < self.limit_real_time:
                hinter_time = self.limit_real_time
            hinter = HinterPostgresTask(task=self.task, source=self.hinter_source, output_path=self.hinter_output_path, limit_real_time=hinter_time, tuples_only=self.tuples_only, align=self.align, ignore_errors=self.ignore_errors) #TODO:version,...
            hint_path = hinter.output_path
            self.steps.append(('hinter', hinter))
        if hint_path and answer_path:
            check = AnswerHintTableDiffTask(hint_path=hint_path, answer_path=answer_path, case_sensitive=self.case_sensitive, space_sensitive=self.space_sensitive, row_delimeter=r'\n', column_delimeter=r'\|', row_sort=self.row_sort, column_sort=self.column_sort, empty_row=False, empty_column=False)
            self.steps.append(('check', check))
        if self.checker_source:
            checker = CheckerPostgresTask(task=self.task, source=self.checker_source, limit_real_time=self.tool_time, ignore_errors=self.checker_ignore_errors) #TODO:version,...
            self.steps.append(('checker', checker))



    def set_system(self, system):
        super().set_system(system)
        for name, step in self.steps:
            step.set_system(system)

    def set_name(self, name):
        super().set_name(name)
        for step_name, step in self.steps:
            step.set_name(name+'_'+step_name)

    def execute(self):
        status = None
        if self.task:
            self.set_result(name='task', value=self.task)
        for name, step in self.steps:
            step_result = step.execute()
            self.set_result(name=name, value=step_result)
            if step_result.status:
                status = step_result.status
                break
        if self.collect_logs:
            time.sleep(1)
            stats = collect_auto_explain(self.resolve_path(self.data_dir)/'log', self.application_name)
            for name,value in stats.items():
                self.set_result(name=name, value=value)

        if self.score:
            self.set_result(name='max_score', value=self.score)
            self.set_result(name='score', value=(self.score if not status else 0))
        self.set_result(status)
        return self.result



class MultipleBuildIOPostgresTask(BuildIOPostgresTask):
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alter_input_path(self, sub, input_path):
        return get_output_path(re.sub(sub[0], sub[1], str(input_path)))

    def create_single(self, input_path):
        test_name = re.sub(*config.MULTITEST_INPUT_NAME, str(input_path))
        test_dir = config.MULTITEST_SINGLE.format(test_name=test_name)
        self.run_command(self.name+'_'+test_name+'_prepare_dir', DirectoryAddCommand, path=test_dir, user_name=config.USER_TEST, group_name=config.USER_TEST)
        generator_output_path = config.MULTITEST_INPUT.format(test_name=test_name)
        hinter_output_path = config.MULTITEST_HINT.format(test_name=test_name)
        answer_path = config.MULTITEST_ANSWER.format(test_name=test_name)

        #TODO:Get values from files
        hint_path = list(self.find_files(self.alter_input_path(config.MULTITEST_INPUT_HINT, input_path)))
        if len(hint_path) > 1:
            #TODO: ?
            pass
        if hint_path:
            hint_path = hint_path[0]
        else:
            hint_path = None

        limit_cores = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_CORES, input_path))
        limit_cores = limit_cores and int(str(limit_cores, 'utf8').strip())
        if not limit_cores:
            limit_cores = self.limit_cores
        limit_time = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_TIME, input_path))
        limit_time = limit_time and parse_time(str(limit_time, 'utf8').strip())
        limit_cpu_time = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_CPU_TIME, input_path))
        limit_cpu_time = limit_cpu_time and parse_time(str(limit_cpu_time, 'utf8').strip())
        limit_cpu_time = limit_cpu_time or limit_time or self.limit_cpu_time
        limit_real_time = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_REAL_TIME, input_path))
        limit_real_time = limit_real_time and parse_time(str(limit_real_time, 'utf8').strip())
        limit_real_time = limit_real_time or limit_time and limit_time+parse_time('1s') or self.limit_real_time
        limit_memory = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_MEMORY, input_path))
        limit_memory = limit_memory and parse_memory(str(limit_memory, 'utf8').strip())
        limit_memory = limit_memory or self.limit_memory
        score = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_SCORE, input_path))
        score = score and float(str(score, 'utf8').strip())
        if score is None:
            score = 1.0

        single = SingleIOPostgresTask(
                executable=self.executable,
                executable_arguments=self.executable_arguments,
                input_path=input_path,
                hint_path=hint_path,
                answer_path=answer_path,
                tool_override=self.tool_override,
                tool_time=self.tool_time,
                generator_source=self.generator_source,
                generator_output_path=generator_output_path,
                verifier_source=self.verifier_source,
                hinter_source=self.hinter_source,
                hinter_output_path=hinter_output_path,
                checker_source=self.checker_source,
                limit_cores=limit_cores,
                limit_cpu_time=limit_cpu_time,
                limit_real_time=limit_real_time,
                limit_memory=limit_memory,
                case_sensitive=self.case_sensitive,
                space_sensitive=self.space_sensitive,
                **self.init_kwargs
            )
        single.set_name(self.name+'_'+test_name)
        single.set_system(self.system)
        return (test_name, single, score)

    def execute(self):
        prepare = PrepareTask(
                source=self.input_path,
                target=config.MULTITEST,
                allow_extract=True,
                user_name = config.USER_TEST,
                group_name = config.USER_TEST,
                result_on_error = 'INT'
                )
        prepare.set_name(self.name+'_prepare')
        prepare.set_system(self.system)
        status = None
        self.run_command(self.name+'_prepare_dir', DirectoryAddCommand, path=prepare.target, user_name=prepare.user_name, group_name=prepare.group_name)
        prepare_result = prepare.execute()
        if prepare_result.status:
            self.set_result(prepare_result.status, 'prepare', prepare_result)
        else:
            singles = []
            for path in self.find_files(prepare.target):
                if path.match(config.MULTITEST_INPUT_GLOB):
                    singles.append(self.create_single(path))
            singles = sorted(singles)

            score = 0.0
            max_score = 0.0
            for step_name, step, step_score in singles:
                step_result = step.execute()
                self.set_result(name='test_'+step_name, value=step_result)
                if not step_result.status:
                    step_result.set_status('OK')
                    score += step_score
                else:
                    if not status:
                        status = step_result.status
                max_score += step_score

            self.set_result(name='score', value=score)
            self.set_result(name='max_score', value=max_score)
            self.set_result(status)
        return self.result


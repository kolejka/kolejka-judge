from commands.mixins import SolutionMixin
from commands.run.base import Run
from validators import ExitCodePostcondition, PSQLErrorPostcondition


class RunPSQL(Run):
    def __init__(self, sql_file, user=None, password=None, host=None, database=None, cmdline_options=None,
                 stdin=None, stdout=None, stderr=None, **kwargs):

        cmdline_options = cmdline_options or []
        if host is not None:
            cmdline_options += ['-h', host]
        if user is not None:
            cmdline_options += ['-U', user]
        if database is not None:
            cmdline_options += ['-d', database]

        super().__init__(executable='psql', cmdline_options=cmdline_options,
                         stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)

        self.sql_file = sql_file
        self.password = password

    def get_env(self):
        env = super().get_env()
        env['PGPASSWORD'] = self.password
        return env

    def get_command(self):
        return [self.executable] + self.cmdline_options + ['--file', self.sql_file]


class RunPSQLSolution(SolutionMixin, RunPSQL):
    def postconditions(self):
        return super().postconditions() + [
            (ExitCodePostcondition(), 'RTE'),
            (PSQLErrorPostcondition(), 'ERROR')
        ]

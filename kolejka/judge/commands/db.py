# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'PSQLCommand', ]
def __dir__():
    return __all__


class PSQLCommand(ProgramCommand):
    DEFAULT_PROGRAM='psql'
    @default_kwargs
    def __init__(self, sql_file=None, sql_user=None, sql_password=None, sql_host=None, sql_database=None, **kwargs):
        super().__init__(**kwargs)
        self.sql_file = sql_file and get_output_path(sql_file)
        self.sql_user = sql_user and str(sql_user)
        self.sql_password = sql_password and str(sql_password)
        self.sql_host = sql_host and str(sql_host)
        self.sql_database = sql_database and str(sql_database)

    def get_environment(self):
        env = super().get_environment()
        if self.sql_password:
            env['PGPASSWORD'] = self.sql_password
        return env

    def get_program_arguments(self):
        args = []
        if self.sql_host:
            args += [ '-h', self.sql_host, ]
        if self.sql_user:
            args += [ '-U', self.sql_user, ]
        if self.sql_database:
            args += [ '-d', self.sql_database, ]
        if self.sql_file:
            args += [ '--file', self.sql_file, ]
        return args

    def get_prerequirements(self):
        return super().get_prerequirements() + [
            FileExistsPrerequirement(self.sql_file),
        ]

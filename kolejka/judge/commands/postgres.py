# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [
    'PInitDBCommand',
    'PostgresCommand',
    'PCreateUserCommand',
    'PDropUserCommand',
    'PCreateDBCommand',
    'PDropDBCommand',
    'PSQLCommand',
    'PSQLAdminCommand',
]
def __dir__():
    return __all__


class PVersionedCommand(ProgramCommand):
    DEFAULT_VERSION=config.POSTGRES_VERSION
    def __init__(self, program, version, **kwargs):
        kwargs['program'] = '/usr/lib/postgresql/%d/bin/%s'%(int(version), program)
        super().__init__(**kwargs)


class PInitDBCommand(PVersionedCommand):
    DEFAULT_PROGRAM='initdb'
    DEFAULT_DATA_DIR=config.POSTGRES_DATA_DIR
    DEFAULT_LOCALE=config.POSTGRES_LOCALE
    DEFAULT_DB_ADMIN=config.POSTGRES_DB_ADMIN
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, data_dir, locale, db_admin, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = data_dir and get_output_path(data_dir)
        self.locale = locale and str(locale)
        self.db_admin = db_admin and str(db_admin)
    def get_program_arguments(self):
        args = []
        args += [ '--pgdata', self.data_dir ]
        args += [ '--auth', 'peer' ]
        if self.locale:
            args += [ '--locale', self.locale ]
        if self.db_admin:
            args += [ '--username', self.db_admin ]
        return args


class PCreateUserCommand(PVersionedCommand):
    DEFAULT_PROGRAM='createuser'
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_DB_ADMIN=config.POSTGRES_DB_ADMIN
    DEFAULT_DB_USER=config.POSTGRES_DB_USER
    DEFAULT_SUPERUSER=False
    DEFAULT_CONNECTION_LIMIT=False
    DEFAULT_ALLOW_LOGIN=True
    DEFAULT_ALLOW_CREATEROLE=False
    DEFAULT_ALLOW_CREATEDB=False
    DEFAULT_ALLOW_REPLICATION=False
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, socket_dir, db_admin, db_user, superuser, allow_login, connection_limit, allow_createdb, allow_createrole, allow_replication, **kwargs):
        super().__init__(**kwargs)
        self.socket_dir = socket_dir and get_output_path(socket_dir)
        self.db_admin = db_admin and str(db_admin)
        self.db_user = db_user and str(db_user)
        self.superuser = bool(superuser)
        self.allow_login = bool(allow_login)
        self.connection_limit = connection_limit and int(connection_limit)
        self.allow_createdb = bool(allow_createdb)
        self.allow_createrole = bool(allow_createrole)
        self.allow_replication = bool(allow_replication)
    def get_program_arguments(self):
        args = []
        args += [ '--host', self.socket_dir ]
        args += [ '--username', self.db_admin, '--no-password' ]
        if self.allow_login:
            args += [ '--login' ]
        else:
            args += [ '--no-login' ]
        if self.connection_limit:
            args += [ '--connection-limit', str(self.connection_limit) ]
        if self.superuser:
            args += [ '--superuser' ]
        else:
            args += [ '--no-superuser' ] 
        if self.allow_createdb:
            args += [ '--createdb' ]
        else:
            args += [ '--no-createdb' ]
        if self.allow_createrole:
            args += [ '--createrole' ]
        else:
            args += [ '--no-createrole' ]
        if self.allow_replication:
            args += [ '--replication' ]
        else:
            args += [ '--no-replication' ]
        args += [ self.db_user ]
        return args


class PDropUserCommand(PVersionedCommand):
    DEFAULT_PROGRAM='dropuser'
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_DB_ADMIN=config.POSTGRES_DB_ADMIN
    DEFAULT_DB_USER=config.POSTGRES_DB_USER
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, socket_dir, db_admin, db_user, **kwargs):
        super().__init__(**kwargs)
        self.socket_dir = socket_dir and get_output_path(socket_dir)
        self.db_admin = db_admin and str(db_admin)
        self.db_user = db_user and str(db_user)
    def get_program_arguments(self):
        args = []
        args += [ '--host', self.socket_dir ]
        args += [ '--username', self.db_admin, '--no-password' ]
        args += [ self.db_user ]
        return args


class PCreateDBCommand(PVersionedCommand):
    DEFAULT_PROGRAM='createdb'
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_DB=config.POSTGRES_DB
    DEFAULT_DB_ADMIN=config.POSTGRES_DB_ADMIN
    DEFAULT_DB_USER=config.POSTGRES_DB_USER
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, socket_dir, db, db_admin, db_user, **kwargs):
        super().__init__(**kwargs)
        self.socket_dir = socket_dir and get_output_path(socket_dir)
        self.db = db and str(db)
        self.db_admin = db_admin and str(db_admin)
        self.db_user = db_user and str(db_user)
    def get_program_arguments(self):
        args = []
        args += [ '--host', self.socket_dir ]
        args += [ '--username', self.db_admin, '--no-password' ]
        args += [ '--owner', self.db_user ]
        args += [ self.db ]
        return args


class PDropDBCommand(PVersionedCommand):
    DEFAULT_PROGRAM='dropdb'
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_DB=config.POSTGRES_DB
    DEFAULT_DB_ADMIN=config.POSTGRES_DB_ADMIN
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, socket_dir, db, db_admin, **kwargs):
        super().__init__(**kwargs)
        self.socket_dir = socket_dir and get_output_path(socket_dir)
        self.db = db and str(db)
        self.db_admin = db_admin and str(db_admin)
    def get_program_arguments(self):
        args = []
        args += [ '--host', self.socket_dir ]
        args += [ '--username', self.db_admin, '--no-password' ]
        args += [ self.db ]
        return args


class PostgresCommand(PVersionedCommand):
    DEFAULT_PROGRAM='postgres'
    DEFAULT_DATA_DIR=config.POSTGRES_DATA_DIR
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_STATISTICS=False
    DEFAULT_AUTO_EXPLAIN=True
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    DEFAULT_BACKGROUND=True

    @default_kwargs
    def __init__(self, data_dir, socket_dir, statistics, auto_explain, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = data_dir and get_output_path(data_dir)
        self.socket_dir = socket_dir and get_output_path(socket_dir)
        self.statistics = bool(statistics)
        self.auto_explain = bool(auto_explain)
    def get_program_arguments(self):
        args = [ '-D', self.data_dir ]
        args += [ '-c', ['unix_socket_directories=',self.socket_dir] ]
        args += [ '-c', 'listen_addresses=' ]
        args += [ '-c', 'logging_collector=true' ]
        args += [ '-c', 'log_destination=csvlog' ]
        args += [ '-c', 'log_directory=log' ]
        args += [ '-c', 'log_filename=log' ]
        args += [ '-c', 'log_connections=true' ]
        if self.auto_explain:
            args += [ '-c', 'shared_preload_libraries=auto_explain' ]
            args += [ '-c', 'auto_explain.log_analyze=true' ]
            args += [ '-c', 'auto_explain.log_format=json' ]
            args += [ '-c', 'auto_explain.log_min_duration=0' ]
        if self.statistics:
            args += [ '-s' ]
        return args


class PSQLCommand(PVersionedCommand):
    DEFAULT_PROGRAM='psql'
    DEFAULT_SOCKET_DIR=config.POSTGRES_SOCKET_DIR
    DEFAULT_DB=config.POSTGRES_DB
    DEFAULT_DB_USER=config.POSTGRES_DB_USER
    DEFAULT_APPLICATION_NAME='psql'
    DEFAULT_QUIET=True
    DEFAULT_TUPLES_ONLY=False
    DEFAULT_ALIGN=True
    DEFAULT_IGNORE_ERRORS=False
    DEFAULT_COMMANDS=[]
    DEFAULT_FILES=[]
    @default_kwargs
    def __init__(self, socket_dir, db, db_user, application_name, quiet, tuples_only, align, ignore_errors, commands, files, **kwargs):
        super().__init__(**kwargs)
        self.socket_dir = socket_dir and get_output_path(socket_dir)
        self.db_user = db_user and str(db_user)
        self.db = db and str(db)
        self.application_name = application_name and str(application_name)
        self.quiet = bool(quiet)
        self.tuples_only = bool(tuples_only)
        self.align = bool(align)
        self.ignore_errors = bool(ignore_errors)
        self._commands = commands and list([str(command) for command in commands]) or list()
        self.files = files and list([get_output_path(fil) for fil in files]) or list()
    def get_program_arguments(self):
        args = []
        args += [ '--no-psqlrc', '--no-readline' ]
        args += [ '--host', self.socket_dir ]
        dbname = 'dbname=%s'%(self.db,)
        if self.application_name:
            dbname += ' application_name=%s'%(self.application_name,)
        args += [ '--dbname', dbname ]
        args += [ '--username', self.db_user, '--no-password' ]
        if self.quiet:
            args += [ '--quiet' ]
        if self.tuples_only:
            args += [ '--tuples-only' ]
        if not self.align:
            args += [ '--no-align' ]
        args += [ '-v', 'ON_ERROR_STOP=%d'%((0 if self.ignore_errors else 1),) ]
        for command in self.commands:
            args += [ '--command', command ]
        for fil in self.files:
            args += [ '--file', fil ]
        return args

    @property
    def commands(self):
        return self.get_commands()
    def get_commands(self):
        return self._commands

class PSQLAdminCommand(PSQLCommand):
    DEFAULT_DB_USER=config.POSTGRES_DB_ADMIN
    DEFAULT_USER=config.USER_POSTGRES
    DEFAULT_GROUP=config.USER_POSTGRES
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

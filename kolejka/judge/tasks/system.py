# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import *


__all__ = [ 'SystemPrepareTask', ]
def __dir__():
    return __all__


class SystemPrepareTask(TaskBase):
    DEFAULT_RECORD_RESULT=False
    @default_kwargs
    def __init__(self, users =config.SYSTEM_USERS, groups =config.SYSTEM_GROUPS, directories =config.SYSTEM_DIRECTORIES, **kwargs):
        super().__init__(**kwargs)
        self.groups = dict()
        self.users = dict()
        self.directories = dict()
        for group in (groups or []):
            self.add_group(group)
        for user in (users or []):
            self.add_user(user)
        for directory in (directories or []):
            self.add_directory(directory)

    def get_nice_name(self, name):
        return str(name).strip().lower()

    def add_group(self, group_name, **kwargs):
        if isinstance(group_name, dict):
            kwargs.update(group_name)
            group_name=kwargs['group_name']
        group_name=self.get_nice_name(group_name)
        kwargs['group_name'] = group_name
        if group_name not in self.groups:
            self.groups[group_name] = kwargs

    def add_user(self, user_name, **kwargs):
        if isinstance(user_name, dict):
            kwargs.update(user_name)
            user_name=kwargs['user_name']
        user_name=self.get_nice_name(user_name)
        kwargs['user_name'] = user_name
        kwargs['groups'] = set([self.get_nice_name(name) for name in list(kwargs.get('groups', []))])
        kwargs['groups'].add(user_name)
        if 'home' in kwargs and kwargs['home']:
            home_path = get_output_path(kwargs['home'])
        if user_name not in self.users:
            for group in kwargs['groups']:
                self.add_group(group)
            self.users[user_name] = kwargs

    def add_directory(self, path, **kwargs):
        if isinstance(path, dict):
            kwargs.update(path)
            path=kwargs['path']
        path=str(get_output_path(path))
        kwargs['path'] = path
        if path not in self.directories:
            if kwargs.get('user_name', None) is not None:
                kwargs['user_name'] = self.get_nice_name(kwargs['user_name'])
                self.add_user(kwargs['user_name'])
            if kwargs.get('group_name', None) is not None:
                kwargs['group_name'] = self.get_nice_name(kwargs['group_name'])
                self.add_group(kwargs['group_name'])
            self.directories[path] = kwargs

    def execute(self):
        for name in self.users.keys():
            if not name in self.system.users:
                self.run_command('usr_del_'+name, UserDelCommand, user_name=name)
        for name in self.groups.keys():
            if not name in self.system.groups:
                self.run_command('grp_del_'+name, GroupDelCommand, group_name=name)
        for group in self.groups.values():
            name = group['group_name']
            if not name in self.system.groups:
                cmd_name = 'grp_'+name
                self.run_command(cmd_name, GroupAddCommand, **group)
                self.system.add_group(name)
        for user in self.users.values():
            name = user['user_name']
            if not name in self.system.users:
                cmd_name = 'usr_'+name
                home = user.get('home', None)
                if home:
                    home = str(self.resolve_path(get_output_path(home)))
                self.run_command(cmd_name, UserAddCommand, **user)
                self.system.add_user(name, home)
        for directory in self.directories.values():
            cmd_name = 'dir_'+str(directory['path']).replace('/', '_')
            self.run_command(cmd_name, DirectoryAddCommand, **directory)
        return self.result

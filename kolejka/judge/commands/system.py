# vim:ts=4:sts=4:sw=4:expandtab
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.commands.base import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *


__all__ = [ 'GroupAddCommand', 'UserAddCommand', 'DirectoryAddCommand', 'InstallCommand', 'ChownDirCommand', 'ChownFileCommand', ]
def __dir__():
    return __all__

class GroupAddCommand(CommandBase):
    def __init__(self, group_name, gid=None, **kwargs):
        super().__init__(**kwargs)
        self.group_name = group_name
        self.gid = gid
    def get_command(self):
        command = []
        if not self.superuser:
            return None
        command += [ 'groupadd', ]
        if self.gid is not None:
            command += [ '--gid', str(self.gid) ]
        command += [ self.group_name ]
        return command
    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement('groupadd'),
        ]

class UserAddCommand(CommandBase):
    def __init__(self, user_name, uid=None, home=None, groups=None, shell=None, comment=None, **kwargs):
        super().__init__(**kwargs)
        self.user_name = user_name
        self.uid = uid
        self.home = home and get_output_path(home)
        self.groups = groups
        self.shell = shell
        self.comment = comment or self.user_name
    def get_command(self):
        command = []
        if not self.superuser:
            return None
        command += [ 'useradd', '--comment', self.comment, ]
        if self.uid is not None:
            command += [ '--uid', str(self.uid) ]
        if self.home:
            command += [ '--create-home', '--home-dir', self.home ]
        else:
            command += [ '--no-create-home' ]
        if self.shell:
            command += [ '--shell', str(self.shell) ]
        if self.groups:
            command += [ '--groups', ','.join([ str(group) for group in self.groups]) ]
        command += [ '--no-user-group', self.user_name ]
        return command
    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement('useradd'),
        ]

class DirectoryAddCommand(CommandBase):
    def __init__(self, path, user_name=None, group_name=None, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.path = get_output_path(path)
        self.user_name = user_name
        self.group_name = group_name
        self.mode = mode
    def get_octal_mode(self):
        if self.mode is None:
            return None
        if isinstance(self.mode, int):
            return '0'+oct(self.mode)[2:]
        return str(self.mode)
    def get_command(self):
        command = [ 'install' ]
        if self.user is not None:
            command += [ '--owner', str(self.user_name) ]
        if self.group is not None:
            command += [ '--group', str(self.group_name) ]
        if self.mode is not None:
            command += [ '--mode', self.get_octal_mode() ]
        command += [ '--directory', str(self.path) ]
        return command
    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement('install'),
            SystemUserExistsPrerequirement(self.user_name),
            SystemGroupExistsPrerequirement(self.group_name),
        ]

class InstallCommand(CommandBase):
    def __init__(self, source, target, user_name=None, group_name=None, mode=None, **kwargs):
        super().__init__(**kwargs)
        self.source = get_output_path(source)
        self.target = get_output_path(target)
        self.user_name = user_name
        self.group_name = group_name
        self.mode = mode
    def get_octal_mode(self):
        if self.mode is None:
            return None
        if isinstance(self.mode, int):
            return '0'+oct(self.mode)[2:]
        return str(self.mode)
    def get_command(self):
        command = [ 'install' ]
        if self.user_name is not None:
            command += [ '--owner', str(self.user_name) ]
        if self.group_name is not None:
            command += [ '--group', str(self.group_name) ]
        if self.mode is not None:
            command += [ '--mode', self.get_octal_mode() ]
        command += [ '--no-target-directory', self.source, self.target ]
        return command
    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement('install'),
            FileExistsPrerequirement(self.source),
            DirectoryExistsPrerequirement(self.target.parent),
            SystemUserExistsPrerequirement(self.user_name),
            SystemGroupExistsPrerequirement(self.group_name),
        ]


class ChownDirCommand(CommandBase):
    def __init__(self, target, recursive=True, user_name=None, group_name=None, **kwargs):
        super().__init__(**kwargs)
        self.target = get_output_path(target)
        self.user_name = user_name
        self.group_name = group_name
        self.recursive = recursive
    def get_command(self):
        command = []
        if not self.superuser:
            return None
        if self.user_name and self.group_name:
            command += [ 'chown', self.user_name+':'+self.group_name, ]
        elif self.user_name:
            command += [ 'chown', self.user_name, ]
        elif self.group_name:
            command += [ 'chgrp', self.group_name, ]
        else:
            return None
        if self.recursive:
            command += [ '--recursive', ]
        command += [ self.target, ]
        return command
    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement('chown'),
            SystemProgramExistsPrerequirement('chgrp'),
            DirectoryExistsPrerequirement(self.target),
            SystemUserExistsPrerequirement(self.user_name),
            SystemGroupExistsPrerequirement(self.group_name),
        ]


class ChownFileCommand(CommandBase):
    def __init__(self, target, user_name=None, group_name=None, **kwargs):
        super().__init__(**kwargs)
        self.target = get_output_path(target)
        self.user_name = user_name
        self.group_name = group_name
    def get_command(self):
        command = []
        if not self.superuser:
            return None
        if self.user_name and self.group_name:
            command += [ 'chown', self.user_name+':'+self.group_name, ]
        elif self.user_name:
            command += [ 'chown', self.user_name, ]
        elif self.group_name:
            command += [ 'chgrp', self.group_name, ]
        else:
            return None
        command += [ self.target, ]
        return command
    def get_prerequirements(self):
        return super().get_prerequirements() + [
            SystemProgramExistsPrerequirement('chown'),
            SystemProgramExistsPrerequirement('chgrp'),
            FileExistsPrerequirement(self.target),
            SystemUserExistsPrerequirement(self.user_name),
            SystemGroupExistsPrerequirement(self.group_name),
        ]

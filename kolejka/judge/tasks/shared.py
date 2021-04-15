# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import *


__all__ = [ 'SharedInstallBinaryTask', 'SharedInstallLibraryTask' ]
def __dir__():
    return __all__

class SharedInstallTask(TaskBase):
    @default_kwargs
    def __init__(self, binary =None, user_name =config.USER_TEST, group_name =config.GROUP_ALL, directory =config.SHARED, **kwargs):
        super().__init__(**kwargs)
        self.user_name = user_name and str(user_name)
        self.group_name = group_name and str(group_name)
        self.directory = directory and get_output_path(directory)

    @property
    def objects(self):
        return self.get_objects()
    def get_objects(self):
        return []

    def execute(self):
        for directory, obj in self.objects:
            directory = directory.strip('/')
            if not self.resolve_path(self.directory / directory).is_dir():
                kwargs = {
                    'path' : self.directory / directory,
                    'user_name' : self.user_name,
                    'group_name' : self.group_name,
                    'mode' : 0o2750,
                }
                cmd_name = 'dir_'+str(kwargs['path']).replace('/', '_')
                self.run_command(cmd_name, DirectoryAddCommand, **kwargs)
            cmd_name = 'install_'+str(obj).replace('/', '_')
            source = obj
            real_source = self.resolve_path(obj)
            target = self.directory / directory / source.name
            mode = 0o640
            if real_source.is_dir() or real_source.is_file() and real_source.stat().st_mode & 0o111:
                mode = 0o750
            self.run_command(cmd_name, InstallCommand, source = source , target = target, user_name = self.user_name, group_name = self.group_name, mode = mode)

class SharedInstallBinaryTask(SharedInstallTask):
    @default_kwargs
    def __init__(self, source =config.SOLUTION_BUILD, binary = '*', user_name =config.USER_TEST, group_name =config.GROUP_ALL, directory =config.SHARED, **kwargs):
        super().__init__(**kwargs)
        self.source = source and get_output_path(source)
        self.binary = binary and str(binary)

    def get_objects(self):
        binaries = []
        for f in self.find_files(self.source):
            if self.resolve_path(f).stat().st_mode & 0o111:
                if f.match('**/'+self.binary):
                    binaries.append( ('bin', f) )
        return binaries

class SharedInstallLibraryTask(SharedInstallTask):
    @default_kwargs
    def __init__(self, source =config.SOLUTION_BUILD, library = '*.so', user_name =config.USER_TEST, group_name =config.GROUP_ALL, directory =config.SHARED, **kwargs):
        super().__init__(**kwargs)
        self.source = source and get_output_path(source)
        self.library = library and str(library)

    def get_objects(self):
        libraries = []
        for f in self.find_files(self.source):
            if f.match('**/'+self.library):
                libraries.append( ('lib', f) )
        return libraries

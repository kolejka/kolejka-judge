import os

from kolejka.judge.commands.base import CommandBase
from kolejka.judge.validators import ProgramExistsPrerequisite, ExitCodePostcondition, FileExistsPrerequisite


class ExtractArchive(CommandBase):
    extensions = ['zip', 'tar', 'tar.gz', 'tar.bz2', '7z', 'rar']

    def __init__(self, archive, archive_type=None, directory='sources'):
        super().__init__()
        self.archive = archive
        self.directory = os.path.join(directory, '')
        self.archive_type = archive_type
        if archive_type is None:
            self.detect_archive_type()

    def get_configuration_status(self):
        return (True, None) if self.archive_type in self.extensions else (False, 'EXT')

    def detect_archive_type(self):
        for extension in self.extensions:
            if self.archive.endswith('.' + extension):
                self.archive_type = extension
                break

    def get_zip_command(self):
        return ['unzip', '-o', '-d', self.directory, self.archive]

    def get_tar_command(self):
        return ['tar', '-xvf', self.archive, '--one-top-level={}'.format(self.directory)]

    def get_tar_gz_command(self):
        return ['tar', '-xzf', self.archive, '--one-top-level={}'.format(self.directory)]

    def get_tar_bz2_command(self):
        return ['tar', '-xjf', self.archive, '--one-top-level={}'.format(self.directory)]

    def get_7z_command(self):
        return ['7z', 'x', self.archive, '-o{}'.format(self.directory), '-y']

    def get_rar_command(self):
        return ['unrar', 'x', self.archive, self.directory, '-y']

    def get_command(self):
        commands = {
            'zip': self.get_zip_command,
            'tar': self.get_tar_command,
            'tar.gz': self.get_tar_gz_command,
            'tar.bz2': self.get_tar_bz2_command,
            '7z': self.get_7z_command,
            'rar': self.get_rar_command,
        }
        return commands[self.archive_type]()

    def prerequisites(self):
        programs = {
            'zip': 'unzip',
            'tar': 'tar',
            'tar.gz': 'tar',
            'tar.bz2': 'tar',
            '7z': '7z',
            'rar': 'unrar',
        }
        return [ProgramExistsPrerequisite(programs[self.archive_type]), FileExistsPrerequisite(self.archive)]

    def postconditions(self):
        return [
            (ExitCodePostcondition(), 'EXT')
        ]

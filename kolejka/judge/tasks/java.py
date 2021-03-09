# vim:ts=4:sts=4:sw=4:expandtab
import os
import re
import shutil
from pathlib import Path


from kolejka.judge import config
from kolejka.judge.typing import *
from kolejka.judge.tasks.base import TaskBase


class RenameJavaFile(TaskBase):
    """
    Taken and adapted from 0ccb87c2bca477080337d9918af853e8.py judge
    """

    @default_kwargs
    def __init__(self, source_file, target_directory='.'):
        self.source_file = Path(source_file)
        self.target_directory = Path(target_directory)

    def execute(self, environment):
        test_class = ''
        with environment.get_path(self.source_file).open() as file:
            for line in file.readlines():
                for p in re.findall(r'^\s*package\s+([^;]+)', line):
                    test_class = p.strip() + '.'
                for c in re.findall(r'^\s*public.+class\s+(\w+)', line):
                    test_class = test_class + c
        parts = test_class.split('.')
        dir = os.path.join('.', *parts[:-1])
        file = parts[-1] + '.java'
        if dir != '.':
            self.target_directory = self.target_directory / dir
        self.target_directory.mkdir(parents=True, exist_ok=True)
        shutil.move(self.source_file, self.target_directory / file)

        return self.result

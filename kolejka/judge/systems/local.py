# vim:ts=4:sts=4:sw=4:expandtab
from contextlib import ExitStack
import datetime
import os
import subprocess
import sys
import tempfile
assert sys.version_info >= (3, 6)


from kolejka.judge.systems.base import *
from kolejka.judge.parse import *


class LocalSystem(SystemBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def get_superuser(self):
        return os.getuid() == 0

    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits, result):
        with ExitStack() as stack:
            stats_file = tempfile.NamedTemporaryFile(mode='r', delete=False)
            stats_file.close()
            os.chmod(stats_file.name, 0o666) 
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.write_file(stdout_path, stdout_append))
            stderr_file = stack.enter_context(self.write_file(stderr_path, stderr_append))

            command = ['/usr/bin/time', '-f', 'mem=%M\nreal=%e\nsys=%S\nuser=%U', '-o', stats_file.name] + command
            process = subprocess.run(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
                preexec_fn=self.get_change_user_function(user=user, group=group),
                cwd=work_path,
            )
            result.set_returncode(process.returncode)

            sys_cpu_time = datetime.timedelta()
            user_cpu_time = datetime.timedelta()
            with open(stats_file.name, 'r') as f:
                for line in f:
                    if line.startswith('mem='):
                        result.update_memory(line.split('=')[-1].strip()+'kb') 
                    if line.startswith('real='):
                        result.update_real_time(line.split('=')[-1].strip()+'s')
                    if line.startswith('sys='):
                        sys_cpu_time = parse_time(line.split('=')[-1].strip()+'s')
                    if line.startswith('user='):
                        user_cpu_time = parse_time(line.split('=')[-1].strip()+'s')
            os.remove(stats_file.name)
            result.update_cpu_time(sys_cpu_time + user_cpu_time)

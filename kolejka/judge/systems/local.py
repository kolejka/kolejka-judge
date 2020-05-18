# vim:ts=4:sts=4:sw=4:expandtab
from contextlib import ExitStack
import datetime
import os
import resource
import signal
import tempfile
import threading
import traceback


from kolejka.judge import config
from kolejka.judge.systems.base import *
from kolejka.judge.parse import *

from kolejka.judge.systems.proc import *

import kolejka.common.subprocess


def monitor_safe_process(process, limits, result):
    while True:
        proc = proc_info(process.pid)
        if proc is None:
            break
        result.update_memory(proc['rss'])
        result.update_real_time(proc['real_time'])
        result.update_cpu_time(proc['cpu_user'] + proc['cpu_sys'])
        if limits.cpu_time and result.cpu_time > limits.cpu_time:
            process.kill()
        if limits.real_time and result.real_time > limits.real_time:
            process.kill()
        if limits.memory and result.memory > limits.memory:
            process.kill()


class LocalSystem(SystemBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def get_superuser(self):
        return os.getuid() == 0

    def execute_safe_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits, result):
        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.write_file(stdout_path, stdout_append))
            stderr_file = stack.enter_context(self.write_file(stderr_path, stderr_append))

            change_user, change_group, change_groups = self.get_user_group_groups(user, group)

            resources = dict()
            if limits.cpu_time:
                resources[resource.RLIMIT_CPU] = (limits.cpu_time,limits.cpu_time)
            if limits.memory:
                resources[resource.RLIMIT_RSS] = (limits.memory,limits.memory)
            resources[resource.RLIMIT_CORE] = (0,0)
            resources[resource.RLIMIT_NPROC] = (1,1)

            process = kolejka.common.subprocess.start(
                command,
                user=change_user,
                group=change_group,
                groups=change_groups,
                resources=resources,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
                cwd=work_path,
            )
            monitoring_thread = threading.Thread(target=monitor_safe_process, args=(process, limits, result))
            monitoring_thread.start()
            returncode = process.wait()
            monitoring_thread.join()
            result.set_returncode(returncode)


    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits, result):
        with ExitStack() as stack:
            stats_file = tempfile.NamedTemporaryFile(mode='r', delete=False)
            stats_file.close()
            os.chmod(stats_file.name, 0o666) 
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.write_file(stdout_path, stdout_append))
            stderr_file = stack.enter_context(self.write_file(stderr_path, stderr_append))
            
            change_user, change_group, change_groups = self.get_user_group_groups(user, group)

            command = ['/usr/bin/time', '-f', 'mem=%M\nreal=%e\nsys=%S\nuser=%U', '-o', stats_file.name] + command
            completed = kolejka.common.subprocess.run(
                command,
                user=change_user,
                group=change_group,
                groups=change_groups,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
                cwd=work_path,
            )
            result.set_returncode(completed.returncode)

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

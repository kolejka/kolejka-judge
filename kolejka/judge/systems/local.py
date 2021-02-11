# vim:ts=4:sts=4:sw=4:expandtab


from contextlib import ExitStack
import datetime
import math
import os
import pwd
import resource
import signal
import tempfile
import time
import threading
import traceback


import kolejka.common.subprocess


from kolejka.judge import config
from kolejka.judge.result import Result
from kolejka.judge.systems.base import *
from kolejka.judge.parse import *

import kolejka.judge.systems.proc as proc


def monitor_safe_process(process, limits, result):
    while True:
        proc_info = proc.info(process.pid)
        if proc_info is None:
            break
        result.update_memory(proc_info['rss'])
        result.update_real_time(proc_info['real_time'])
        result.update_cpu_time(proc_info['cpu_user'] + proc_info['cpu_sys'])
        if limits.cpu_time and result.cpu_time > limits.cpu_time:
            process.kill()
        if limits.real_time and result.real_time > limits.real_time:
            process.kill()
        if limits.memory and result.memory > limits.memory:
            process.kill()

def end_process(process):
    try:
        pids = proc.descendants(process.pid)
        try:
            process.terminate()
            time.sleep(0.1)
        except:
            pass
        for pid in pids:
            try:
                os.kill(pid)
            except:
                pass
        while True:
            pids = proc.descendants(process.pid)
            if pids:
                for pid in pids:
                    try:
                        os.kill(pid)
                    except:
                        pass
            else:
                break
    except:
        pass

def monitor_process(process, limits, result):
    real_time = dict()
    cpu_time = dict()
    while True:
        proc_info = proc.info(process.pid)
        if proc_info is None:
            break
        memory = proc_info['rss']
        real_time[process.pid] = proc_info['real_time']
        cpu_time[process.pid] = proc_info['cpu_user'] + proc_info['cpu_sys']

        proc_info = dict([ (pid, proc.info(pid)) for pid in proc.descendants(process.pid) ])
        for pid, info in proc_info.items():
            if info is None:
                continue
            memory += info['rss']
            real_time[pid] = max(real_time.get(pid,0), info['real_time'])
            cpu_time[pid] = max(cpu_time.get(pid,0), info['cpu_user'] + info['cpu_sys'])

        result.update_memory(memory)
        result.update_real_time(sum(real_time.values()))
        result.update_cpu_time(sum(cpu_time.values()))
        if limits.cpu_time and result.cpu_time > limits.cpu_time:
            end_process(process)
        if limits.real_time and result.real_time > limits.real_time:
            end_process(process)
        if limits.memory and result.memory > limits.memory:
            end_process(process)

class LocalSystem(SystemBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def get_superuser(self):
        return os.getuid() == 0

    def get_current_user(self):
        return pwd.getpwuid(os.getuid()).pw_name

    def get_resources(self, limits):
        resources = dict()
        for limit in [
                resource.RLIMIT_CORE,
                resource.RLIMIT_CPU,
#                resource.RLIMIT_FSIZE,
                resource.RLIMIT_DATA,
                resource.RLIMIT_STACK,
#                resource.RLIMIT_RSS,
#                resource.RLIMIT_NPROC,
#                resource.RLIMIT_NOFILE,
#                resource.RLIMIT_MEMLOCK,
#                resource.RLIMIT_AS,
#                resource.RLIMIT_MSGQUEUE,
#                resource.RLIMIT_NICE,
#                resource.RLIMIT_RTPRIO,
#                resource.RLIMIT_RTTIME,
#                resource.RLIMIT_SIGPENDING,
                ]:
            resources[limit] = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)

        resources[resource.RLIMIT_CORE] = (0,0)

        if limits.cpu_time:
            seconds = int(math.ceil((limits.cpu_time + parse_time('1s')).total_seconds()))
            resources[resource.RLIMIT_CPU] = (seconds, seconds)

        if limits.memory:
            memory = int(math.ceil(limits.memory + parse_memory('1mb')))
            resources[resource.RLIMIT_DATA] = (limits.memory,limits.memory)

        return resources


    def execute_safe_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result):
        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes))
            stderr_file = stack.enter_context(self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes))

            change_user, change_group, change_groups = self.get_user_group_groups(user, group)

            resources = self.get_resources(limits)
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


    def start_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits):
        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes))
            stderr_file = stack.enter_context(self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes))
            
            change_user, change_group, change_groups = self.get_user_group_groups(user, group)

            resources = self.get_resources(limits)

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
            result = Result() 
            monitoring_thread = threading.Thread(target=monitor_process, args=(process, limits, result))
            monitoring_thread.start()
            return (process, monitoring_thread, result)

    def terminate_command(self, process):
        process, monitoring_thread, monitor_result = process
        process.terminate()

    def wait_command(self, process, result):
        process, monitoring_thread, monitor_result = process
        completed = kolejka.common.subprocess.wait(process)
        monitoring_thread.join()
        result.update_memory(monitor_result.memory)
        result.update_real_time(monitor_result.real_time)
        result.update_cpu_time(monitor_result.cpu_time)
        result.set_returncode(completed.returncode)

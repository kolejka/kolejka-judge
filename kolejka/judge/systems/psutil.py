# vim:ts=4:sts=4:sw=4:expandtab


from contextlib import ExitStack
import math
import os
import resource
import threading
import time


import kolejka.common.subprocess


from kolejka.judge import config
from kolejka.judge.systems.local import LocalSystem


def monitor_process(process, limits, result):
    import psutil
    try:
        if limits.cores:
            process.cpu_affinity(range(limits.cores))
        while True:
            with process.oneshot():
                result.update_memory(process.memory_info().vms)
                result.update_real_time(time.time() - process.create_time())
                cpu_times = process.cpu_times()
                result.update_cpu_time(cpu_times.user + cpu_times.system)
                result.update_cpu_time(cpu_times.user + cpu_times.system + cpu_times.children_user + cpu_times.children_system)

            if limits.cpu_time and result.cpu_time > limits.cpu_time:
                process.kill()
            if limits.real_time and result.real_time > limits.real_time:
                process.kill()
            if limits.memory and result.memory > limits.memory:
                process.kill()
            if limits.pids and len(process.children(recursive=True)) > limits.pids:
                process.kill()

            time.sleep(0.1)

    except psutil.NoSuchProcess:
        pass


class PsutilSystem(LocalSystem):
    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits, result):
        import psutil
        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.write_file(stdout_path, stdout_append))
            stderr_file = stack.enter_context(self.write_file(stderr_path, stderr_append))

            change_user, change_group, change_groups = self.get_user_group_groups(user, group)

            resources = dict()
            if limits.cpu_time:
                seconds = int(math.ceil(limits.cpu_time.total_seconds()))
                resources[resource.RLIMIT_CPU] = (seconds, seconds)
            if limits.memory:
                resources[resource.RLIMIT_DATA] = (limits.memory,limits.memory)
            resources[resource.RLIMIT_CORE] = (0,0)

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
            process = psutil.Process(process.pid)
            monitoring_thread = threading.Thread(target=monitor_process, args=(process, limits, result))
            monitoring_thread.start()
            returncode = process.wait()
            monitoring_thread.join()
            result.set_returncode(returncode)

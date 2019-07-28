# vim:ts=4:sts=4:sw=4:expandtab
from contextlib import ExitStack
import os
import sys
import threading
import time
assert sys.version_info >= (3, 6)


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

            process = psutil.Popen(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
                preexec_fn=self.get_change_user_function(user=user, group=group),
                cwd=work_path,
            )
            monitoring_thread = threading.Thread(target=monitor_process, args=(process, limits, result))
            monitoring_thread.start()
            process.wait()
            monitoring_thread.join()
            result.set_returncode(process.returncode)

# vim:ts=4:sts=4:sw=4:expandtab


from contextlib import ExitStack
from copy import deepcopy
import os
import random
import string
import subprocess
import threading
import time


from kolejka.judge import config
from kolejka.judge.systems.local import LocalSystem


def monitor_process(unit, superuser, limits, result):
    start_time = time.perf_counter()
    systemctl = [ 'systemctl' ]
    if not superuser:
        systemctl += [ '--user' ]
    try: 
        while True:
            show_run = subprocess.run(systemctl + [ 'show', unit, ], stdout=subprocess.PIPE)
            show = dict()
            for line in show_run.stdout.split(b'\n'):
                line = line.split(b'=')
                if len(line) > 1:
                    key = line[0]
                    val = b'='.join(line[1:])
                    show[key.decode()] = val.decode().strip()
            if show.get('ActiveState', None) == 'active' and show.get('SubState', None) == 'exited':
                break
            if show.get('ActiveState', None) == 'failed' and show.get('SubState', None) == 'failed':
                break
            
            try:
                memory_current = int(show.get('MemoryCurrent', 0))
                result.update_memory(str(memory_current)+'b')
            except:
                pass

            try:
                cpu_usage = int(show.get('CPUUsageNSec', 0))
                result.update_cpu_time(str(cpu_usage)+'ns')
            except:
                pass

            result.update_real_time(time.perf_counter() - start_time)

            if limits.cpu_time and result.cpu_time > limits.cpu_time:
                break
            if limits.real_time and result.real_time > limits.real_time:
                break
            if limits.memory and result.memory > limits.memory:
                break

            time.sleep(0.1)
    finally:
        subprocess.run(systemctl + [ 'reset-failed', unit, ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(systemctl + [ 'stop', unit, ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SystemdSystem(LocalSystem):
    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result):
        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes))
            stderr_file = stack.enter_context(self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes))

            unit = 'kolejka-judge-unit-'+''.join(random.choices(string.ascii_lowercase, k=16))+'.service'
            systemd = [ 'systemd-run', ]
            if not self.superuser:
                systemd += [ '--user', ]
            systemd += [ '--unit', unit, '--remain-after-exit', '--quiet', '--pipe', '-p', 'CPUAccounting=true', '-p', 'MemoryAccounting=true', ]
            systemd += [ '-p', 'WorkingDirectory=%s'%(work_path,), ]
            if limits.memory:
                systemd += [ '-p', 'MemoryMax=%d'%(limits.memory,), ]
            if limits.pids:
                systemd += [ '-p', 'TasksMax=%d'%(limits.pids,), ]
            if limits.cores:
                systemd += [ '-p', 'CPUAffinity=%s'%(' '.join([ '%d'%(c,) for c in range(limits.cores)]),), ]
            change_user, change_group, change_groups = self.get_user_group_groups(user, group)
            if change_user:
                systemd += [ '-p', 'User=%d'%(change_user,), ]
            if change_group:
                systemd += [ '-p', 'Group=%d'%(change_group,), ]
            if change_groups:
                systemd += [ '-p', 'SupplementaryGroups=%s'%(' '.join([ '%d'%(g,) for g in change_groups ])), ]
            if self.superuser:
                systemd += [ '-p', 'PassEnvironment=', ]
                systemd += [ '-p', 'UnsetEnvironment=INVOCATION_ID LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION LC_ALL', ]
                for key, val in environment.items():
                    systemd += [ '-p', 'Environment="%s=%s"'%(key,val), ]
            else:
                systemd_env = [ 'env', '-i', ] + [ '%s=%s'%(key,val) for key,val in environment.items() ]
                systemd += systemd_env

            process = subprocess.Popen(
                systemd + command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
            )
            monitoring_thread = threading.Thread(target=monitor_process, args=(unit, self.superuser, limits, result))
            monitoring_thread.start()
            process.wait()
            monitoring_thread.join()
            result.set_returncode(process.returncode)

# vim:ts=4:sts=4:sw=4:expandtab
from contextlib import ExitStack
import os
import random
import string
import subprocess
import sys
import threading
import time
assert sys.version_info >= (3, 6)


from kolejka.judge.systems.local import LocalSystem

def monitor_process(unit, limits, result):
    start_time = time.perf_counter()
    try: 
        while True:
            show_run = subprocess.run([ 'systemctl', 'show', unit, ], stdout=subprocess.PIPE)
            show = dict()
            for line in show_run.stdout.split(b'\n'):
                line = line.split(b'=')
                if len(line) > 1:
                    key = line[0]
                    val = b'='.join(line[1:])
                    show[key.decode()] = val.decode().strip()
            if show.get('ActiveState') == 'active' and show.get('SubState', None) == 'exited':
                break
            if show.get('ActiveState') == 'failed' and show.get('SubState', None) == 'failed':
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
        subprocess.run([ 'systemctl', 'reset-failed', unit, ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([ 'systemctl', 'stop', unit, ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SystemdSystem(LocalSystem):
    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stderr_path, stderr_append, environment, work_path, user, group, limits, result):
        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.write_file(stdout_path, stdout_append))
            stderr_file = stack.enter_context(self.write_file(stderr_path, stderr_append))

            unit = 'kolejka-judge-unit-'+''.join(random.choices(string.ascii_lowercase, k=16))+'.service'
            systemd = [ 'systemd-run', '--unit', unit, '--remain-after-exit', '--quiet', '--pipe', '-p', 'CPUAccounting=true', '-p', 'MemoryAccounting=true', ]
            systemd += [ '-p', 'PassEnvironment=true', ]
            systemd += [ '-p', 'WorkingDirectory=%s'%(work_path,), ]
            if limits.memory:
                systemd += [ '-p', 'MemoryMax=%d'%(limits.memory,), ]
            if limits.pids:
                systemd += [ '-p', 'TasksMax=%d'%(limits.pids,), ]
            if limits.cores:
                systemd += [ '-p', 'CPUAffinity=%s'%(' '.join([ '%d'%(c,) for c in range(limits.cores)]),), ]
            uid, gid, groups = self.get_uid_gid_groups(user=user, group=group)
            if uid:
                systemd += [ '-p', 'User=%d'%(uid,), ]
            if gid:
                systemd += [ '-p', 'Group=%d'%(gid,), ]
            if groups:
                systemd += [ '-p', 'SupplementaryGroups=%s'%(' '.join([ '%d'%(g,) for g in groups ])), ]
            process = subprocess.Popen(
                systemd + command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
            )
            monitoring_thread = threading.Thread(target=monitor_process, args=(unit, limits, result))
            monitoring_thread.start()
            process.wait()
            monitoring_thread.join()
            result.set_returncode(process.returncode)

# vim:ts=4:sts=4:sw=4:expandtab


import datetime
import math
import os
import pathlib
import pwd
import resource
import signal
import tempfile
import time
import threading
import traceback


import kolejka.common.subprocess
from kolejka.common.gpu import gpu_stats

from kolejka.judge import config
from kolejka.judge.result import Result
from kolejka.judge.systems.base import *
from kolejka.judge.parse import *


__all__ = [ 'LocalSystem' ]
def __dir__():
    return __all__


page_size = int(os.sysconf("SC_PAGE_SIZE"))
clock_ticks = int(os.sysconf("SC_CLK_TCK"))

def proc_info(pid):
    proc = pathlib.Path('/proc/'+str(pid))
    with pathlib.Path('/proc/uptime').open() as uptime_file:
        uptime = float(uptime_file.read().strip().split()[0])
    try:
        with ( proc / 'stat' ).open() as stat_file:
            stat = stat_file.read().strip().split()
        with ( proc / 'statm' ).open() as statm_file:
            statm = statm_file.read().strip().split()
        with ( proc / 'io' ).open() as io_file:
            io = dict( [ (k.strip().lower(), int(v.strip())) for k,v in [ l.split(':') for l in io_file.read().strip().split('\n') ] ] )

        result = dict()
        result['ppid'] = int(stat[3])
        result['cpu_user'] = int(stat[13]) / clock_ticks
        result['cpu_sys'] = int(stat[14]) / clock_ticks
        result['rss'] = int(statm[1]) * page_size
        result['threads'] = int(stat[19])
        result['read'] = io['rchar']
        result['write'] = io['wchar']
        result['real_time'] = uptime - int(stat[21]) / clock_ticks
        return result
    except:
        return None

def proc_ppid(pid):
    proc = pathlib.Path('/proc/'+str(pid))
    try:
        with ( proc / 'stat' ).open() as stat_file:
            stat = stat_file.read().strip().split()
            return int(stat[3])
    except:
        return None

def proc_pids():
    proc = pathlib.Path('/proc')
    return [ int(p.name) for p in proc.iterdir() if p.is_dir() and not p.is_symlink() and p.name.isdigit() ] 

def proc_ppids():
    result = dict()
    for p in proc_pids():
        pp = proc_ppid(p)
        if pp is not None:
            result[p] = pp
    return result

def proc_children(pid):
    return [ p for p in proc_pids() if proc_ppid(p) == pid ]

def proc_descendants(pid):
    parents = proc_ppids()
    children = dict([ (p,list()) for p in parents.values() ])
    for child, parent in parents.items():
        children[parent].append(child)
    new_descendants = [ pid ]
    all_descendants = []
    while new_descendants:
        active = new_descendants
        new_descendants = []
        for p in active:
            all_descendants += children.get(p,[])
            new_descendants += children.get(p,[])
    return all_descendants

def monitor_safe_process(process, limits, result):
    while True:
        info = proc_info(process.pid)
        if info is None:
            break
        result.update_memory(info['rss'])
        result.update_real_time(info['real_time'])
        result.update_cpu_time(info['cpu_user'] + info['cpu_sys'])
        if limits.cpu_time and result.cpu_time > limits.cpu_time:
            process.kill()
        if limits.real_time and result.real_time > limits.real_time:
            process.kill()
        if limits.memory and result.memory > limits.memory:
            process.kill()
        time.sleep(0.05)

def end_process(process):
    try:
        pids = proc_descendants(process.pid)
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
            pids = proc_descendants(process.pid)
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
        info = proc_info(process.pid)
        if info is None:
            break
        memory = info['rss']
        real_time[process.pid] = info['real_time']
        cpu_time[process.pid] = info['cpu_user'] + info['cpu_sys']

        infos = dict([ (pid, proc_info(pid)) for pid in proc_descendants(process.pid) ])
        for pid, info in infos.items():
            if info is None:
                continue
            memory += info['rss']
            real_time[pid] = max(real_time.get(pid,0), info['real_time'])
            cpu_time[pid] = max(cpu_time.get(pid,0), info['cpu_user'] + info['cpu_sys'])

        result.update_memory(memory)
        result.update_real_time(sum(real_time.values()))
        result.update_cpu_time(sum(cpu_time.values()))

        gpu_memory = 0
        for gpu, stats in gpu_stats().dump().get('gpus').items():
            usage = parse_memory(stats.get('memory_usage'))
            if limits.gpu_memory:
                total = parse_memory(stats.get('memory_total'))
                gpu_memory = max(gpu_memory, limits.gpu_memory - (total - usage))
            else:
                gpu_memory = max(gpu_memory, usage)

        result.update_gpu_memory(gpu_memory)

        if limits.cpu_time and result.cpu_time > limits.cpu_time:
            end_process(process)
        if limits.real_time and result.real_time > limits.real_time:
            end_process(process)
        if limits.memory and result.memory > limits.memory:
            end_process(process)
        if limits.gpu_memory and result.gpu_memory > limits.gpu_memory:
            end_process(process)
        time.sleep(0.05)

class LocalSystem(SystemBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.preserved_gpu_memory = {}

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

    def preserve_gpu_memory(self, memory_limit: int) -> None:
        """
        Preserves every GPU to have at most desired memory free
        """
        try:
            import numpy as np
            from numba import cuda
            from numba.cuda.cudadrv.driver import CudaAPIError, Device
        except ImportError:
            raise RuntimeError("Numba is required to limit GPU memory")

        ARRAY_ELEMENT_DTYPE = np.uint8
        ARRAY_ELEMENT_SIZE = np.dtype(ARRAY_ELEMENT_DTYPE).itemsize

        self.preserved_gpu_memory = {}
        for gpu_index, gpu in enumerate(cuda.gpus.lst):
            with gpu:
                # Initialize CUDA context preserves minor amount of memory to be allocated
                _ = cuda.device_array((1,))

                # Retrieve current device free memory space (in bytes)
                bytes_free, bytes_total = cuda.current_context().get_memory_info()

                bytes_to_preserve = bytes_free - memory_limit

                if bytes_to_preserve < 0:
                    raise RuntimeError(f"Not enough memory on {repr(gpu)} requested {bytes_to_preserve}")

                if bytes_to_preserve > 0:
                    try:
                        self.preserved_gpu_memory[gpu_index] = cuda.device_array(
                            (bytes_to_preserve // ARRAY_ELEMENT_SIZE,),
                            dtype=ARRAY_ELEMENT_DTYPE
                        )
                    except CudaAPIError as e:
                        raise RuntimeError(f"CUDA operation failure: {e}")

    def release_gpu_memory(self):
        for gpu, memory in self.preserved_gpu_memory.items():
            del memory

    def execute_safe_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result):
        stdin_file = self.read_file(stdin_path)
        stdout_file, stdout_writer = self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes)
        stderr_file, stderr_writer = self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes)
        writers = (stdout_writer, stderr_writer)

        change_user, change_group, change_groups = self.get_user_group_groups(user, group)

        resources = self.get_resources(limits)
        #resources[resource.RLIMIT_NPROC] = (1,1) #This is a very bad idea, read notes in man execv on EAGAIN

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
        stdin_file.close()
        stdout_file.close()
        stderr_file.close()
        monitoring_thread = threading.Thread(target=monitor_safe_process, args=(process, limits, result))
        monitoring_thread.start()
        returncode = process.wait()
        monitoring_thread.join()
        for writer in writers:
            writer.join()
        result.set_returncode(returncode)


    def start_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits):
        stdin_file = self.read_file(stdin_path)
        stdout_file, stdout_writer = self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes)
        stderr_file, stderr_writer = self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes)
        writers = (stdout_writer, stderr_writer)
        
        change_user, change_group, change_groups = self.get_user_group_groups(user, group)

        resources = self.get_resources(limits)

        if limits.gpu_memory:
            self.preserve_gpu_memory(limits.gpu_memory)

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
        stdin_file.close()
        stdout_file.close()
        stderr_file.close()
        result = Result()
        monitoring_thread = threading.Thread(target=monitor_process, args=(process, limits, result))
        monitoring_thread.start()
        return (process, monitoring_thread, result, writers)

    def terminate_command(self, process):
        process, monitoring_thread, monitor_result, writers = process
        process.terminate()
        for writer in writers:
            writer.join()
        self.release_gpu_memory()

    def wait_command(self, process, result):
        process, monitoring_thread, monitor_result, writers = process
        completed = kolejka.common.subprocess.wait(process)
        monitoring_thread.join()
        for writer in writers:
            writer.join()
        result.update_memory(monitor_result.memory)
        result.update_real_time(monitor_result.real_time)
        result.update_cpu_time(monitor_result.cpu_time)
        result.update_gpu_memory(monitor_result.gpu_memory)
        result.update_real_time(completed.time)
        result.set_returncode(completed.returncode)
        self.release_gpu_memory()

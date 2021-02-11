# vim:ts=4:sts=4:sw=4:expandtab


from contextlib import ExitStack
import resource


from kolejka.judge import config
from kolejka.judge.systems.local import LocalSystem
from kolejka.judge.parse import *


class ObserverSystem(LocalSystem):

    def start_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits):
        import kolejka.observer.runner
        from kolejka.common import KolejkaLimits

        change_user, change_group, change_groups = self.get_user_group_groups(user, group)

        resources = self.get_resources(limits)
        limits=KolejkaLimits(
                    cpus=limits.cores,
                    memory=limits.memory,
                    swap=0,
                    pids=limits.pids,
                    time=limits.real_time,
                )
        #TODO: cpu_time !!!!!

        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes))
            stderr_file = stack.enter_context(self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes))
            process = kolejka.observer.runner.start(
                command,
                limits=limits,
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
        return process

    def terminate_command(self, process):
        process.terminate()

    def wait_command(self, process, result):
        import kolejka.observer.runner
        completed = kolejka.observer.runner.wait(process)
        result.set_returncode(completed.returncode)
        result.update_memory(completed.stats.memory.max_usage)
        result.update_cpu_time(completed.stats.cpu.usage)

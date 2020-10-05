# vim:ts=4:sts=4:sw=4:expandtab


from contextlib import ExitStack


from kolejka.judge import config
from kolejka.judge.systems.local import LocalSystem


class ObserverSystem(LocalSystem):
    def execute_command(self, command, stdin_path, stdout_path, stdout_append, stdout_max_bytes, stderr_path, stderr_append, stderr_max_bytes, environment, work_path, user, group, limits, result):
        from kolejka import observer
        from kolejka.common import KolejkaLimits

        change_user, change_group, change_groups = self.get_user_group_groups(user, group)

        with ExitStack() as stack:
            stdin_file = stack.enter_context(self.read_file(stdin_path))
            stdout_file = stack.enter_context(self.file_writer(stdout_path, stdout_append, max_bytes=stdout_max_bytes))
            stderr_file = stack.enter_context(self.file_writer(stderr_path, stderr_append, max_bytes=stderr_max_bytes))
            process = observer.run(
                command,
                stdin=stdin_file,
                stdout=stdout_file,
                stderr=stderr_file,
                env=environment,
                limits=KolejkaLimits(
                    cpus=limits.cores,
                    memory=limits.memory,
                    swap=0,
                    pids=limits.pids,
                    time=limits.real_time
                    ),
                user=change_user,
                group=change_group,
                groups=change_groups,
                cwd=work_path,
            )
            result.set_returncode(process.returncode)
            result.update_memory(process.stats.memory.max_usage)
            result.update_cpu_time(process.stats.cpu.usage)

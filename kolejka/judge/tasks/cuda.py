# vim:ts=4:sts=4:sw=4:expandtab

import io
import csv
import shutil
from typing import List, Optional

from kolejka.judge import config
from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.io import *
from kolejka.judge.typing import default_kwargs
from kolejka.judge.commands import ExecutableCommand
from kolejka.judge.tasks.tools import ToolTask
from kolejka.judge.result import Result

__all__ = [ 'ExecutableCudaTask', 'SolutionExecutableCudaTask', 
            'ProgramCudaTask', 'SolutionProgramCudaTask',
            'SingleIOCudaTask', 'MultipleIOCudaTask' ]

def __dir__():
    return __all__

NVIDIA_NSIGHT_PATH = '/usr/local/bin/nv-nsight-cu-cli'

NVIDIA_NSIGHT_DEFAULT_ARGS = [
    # '--summary', 'per-gpu',
    '--csv',
    '--print-units', 'base',
    '--print-fp',
    '--force-overwrite',
    '--target-processes', 'all',
]

class ExecutableCudaTask(ExecutableTask):
    @default_kwargs
    def __init__(
            self,
            cuda_metrics: Optional[List[str]] = None,
            cuda_profile_log: Optional[str] = None,
            **kwargs
    ):
        super().__init__(**kwargs)

        self._cuda_metrics = cuda_metrics
        self._cuda_profile_log = cuda_profile_log or 'profiler_metrics.txt'

    def get_executable(self):
        if self._cuda_metrics:
            return NVIDIA_NSIGHT_PATH

        return super().get_executable()

    def get_executable_arguments(self):
        if self._cuda_metrics:
            metrics = ','.join(self._cuda_metrics)

            # metrics = 'all'

            return NVIDIA_NSIGHT_DEFAULT_ARGS + \
                   ['--log-file', self._cuda_profile_log, '--metrics', metrics] + \
                   [super().get_executable()] + \
                   super().get_executable_arguments()

        return super().get_executable_arguments()

    def _sparse_metric(self, functor: str, values: dict):
        print('SPARCE METRIC', values)
        if functor == 'sum':
            operator = sum
        elif functor == 'max':
            operator = max
        elif functor == 'min':
            operator = min
        elif functor == 'avg':
            operator = lambda x: sum(x)/len(x)
        else:
            operator = lambda x: 0

        return operator(map(float, values.values()))

    def _parse_metrics(self):
        # TODO: Change to task
        with open('RES/1/test/profiler') as handler:
            data = handler.readlines()

        data = ''.join(list(filter(lambda line: not line.startswith('==PROF=='), data)))

        print(data)

        metrics_csv = io.StringIO(data)
        data = csv.DictReader(metrics_csv)
        from collections import defaultdict
        stats = defaultdict(dict)
        for row in data:
            device, pid, name, value = row['ID'], row['Process ID'], row['Metric Name'], row['Metric Value']
            stats[device][name] = stats.get(device, {})
            stats[device][name].update({
                f'{pid}': str(value)
            })

        out = {}

        for gpu, metric_kv in stats.items():
            print(gpu, metric_kv)
            out[gpu] = {}
            for name, values in metric_kv.items():
                functor = name.split('.')[-1]
                out[gpu][name] = self._sparse_metric(functor, values)

        print(out)

        return {}

    def execute(self):
        result = self.run_command(
            'run',
            ExecutableCommand,
            executable=self.executable,
            executable_arguments=self.executable_arguments
        )

        self._parse_metrics()

        self.set_result(result)
        return self.result

class SolutionExecutableCudaTask(SolutionExecutableTask, ExecutableCudaTask):
    pass

class ProgramCudaTask(ProgramTask):
    pass

class SolutionProgramCudaTask(SolutionProgramTask):
    pass

class SingleIOCudaTask(SingleIOTask):
    DEFAULT_CUDA_PROFILE_LOG = config.CUDA_PROFILER

    @default_kwargs
    def __init__(
            self,
            cuda_metrics: Optional[List[str]] = None,
            cuda_profile_log: Optional[str] = None,
            **kwargs
    ):
        print('default = ', cuda_profile_log)
        self._cuda_metrics = cuda_metrics
        self._cuda_profile_log = cuda_profile_log

        super().__init__(**kwargs)

    def solution_task_factory(self, **kwargs):
        return SolutionExecutableCudaTask(
            cuda_metrics=self._cuda_metrics,
            cuda_profile_log=self._cuda_profile_log,
            **kwargs
        )

class MultipleIOCudaTask(MultipleIOTask):
    pass

# vim:ts=4:sts=4:sw=4:expandtab

import io
import csv
from typing import List, Optional
from collections import defaultdict

from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.io import *
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.commands import *

__all__ = [ 'ExecutableCudaTask', 'SolutionExecutableCudaTask',
            'SingleIOCudaTask' ]

def __dir__():
    return __all__

NVIDIA_NSIGHT_PATH = 'nv-nsight-cu-cli'

NVIDIA_NSIGHT_DEFAULT_ARGS = [
    '--quiet',
    '--print-units', 'base',
    '--print-fp',
    '--force-overwrite',
    '--target-processes', 'all'
]

class ExecutableCudaTask(ExecutableTask):
    def __init__(
            self,
            cuda_metrics: Optional[List[str]] = None,
            cuda_profile_log: Optional[str] = None,
            cuda_metrics_output: Optional[str] = None,
            **kwargs
    ):
        super().__init__(**kwargs)

        self._cuda_metrics = cuda_metrics
        self._cuda_profile_log = cuda_profile_log and get_output_path(cuda_profile_log)
        self._cuda_metrics_output = cuda_metrics_output and get_output_path(cuda_metrics_output)

    def _aggregate_metric(self, name: str, values: list):
        functor = name.split('.')[-1]

        if functor == 'sum':
            return sum(values)
        if functor == 'max':
            return max(values)
        if functor == 'min':
            return min(values)
        return sum(values) / len(values)

    def _parse_metrics(self, path):
        stats = defaultdict(list)
        metrics_data = str(self.file_contents(path), 'utf-8')

        for row in csv.DictReader(io.StringIO(metrics_data)):
            name, value = row['Metric Name'], row['Metric Value']
            stats[name].append(float(value.replace(',', '')))

        return {
            f'{metric}': self._aggregate_metric(metric, value)
            for metric, value in stats.items()
        }

    def execute(self):
        if self._cuda_metrics:
            metrics = ','.join(self._cuda_metrics)

            self.run_command(
                'run',
                ProgramCommand,
                program=NVIDIA_NSIGHT_PATH,
                program_arguments=NVIDIA_NSIGHT_DEFAULT_ARGS +
                                  ['--export', self._cuda_profile_log, '--metrics', metrics] +
                                  [super().get_executable()] + super().get_executable_arguments()
            )

            self.run_command(
                'profiler',
                ProgramCommand,
                program=NVIDIA_NSIGHT_PATH,
                program_arguments=[
                    '--csv',
                    '--import', self._cuda_profile_log
                ],
                stdout=self._cuda_metrics_output
            )

            metrics = self._parse_metrics(self.commands.get('profiler').stdout_path)

            for metric_name, metric_value in metrics.items():
                self.set_result(None, metric_name, f'{metric_value:.4f}')

            return self.result

        return super().execute()

class SolutionExecutableCudaTask(ExecutableCudaTask, SolutionExecutableTask):
    pass

class SingleIOCudaTask(SingleIOTask):
    DEFAULT_CUDA_PROFILE_LOG = config.CUDA_PROFILER
    DEFAULT_CUDA_METRICS_OUTPUT = config.CUDA_METRICS

    @default_kwargs
    def __init__(
            self,
            cuda_metrics: Optional[List[str]] = None,
            cuda_profile_log: Optional[str] = None,
            cuda_metrics_output: Optional[str] = None,
            **kwargs
    ):
        self._cuda_metrics = cuda_metrics
        self._cuda_profile_log = cuda_profile_log
        self._cuda_metrics_output = cuda_metrics_output

        super().__init__(**kwargs)

    def solution_task_factory(self, **kwargs):
        return SolutionExecutableCudaTask(
            cuda_metrics=self._cuda_metrics,
            cuda_profile_log=self._cuda_profile_log,
            cuda_metrics_output=self._cuda_metrics_output,
            **kwargs
        )

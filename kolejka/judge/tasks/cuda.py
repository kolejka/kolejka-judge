# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.io import *


__all__ = [ 'ExecutableCudaTask', 'SolutionExecutableCudaTask', 
            'ProgramCudaTask', 'SolutionProgramCudaTask',
            'SingleIOCudaTask', 'MultipleIOCudaTask' ]
def __dir__():
    return __all__

class ExecutableCudaTask(ExecutableTask):
    pass
class SolutionExecutableCudaTask(SolutionExecutableTask):
    pass
class ProgramCudaTask(ProgramTask):
    pass
class SolutionProgramCudaTask(SolutionProgramTask):
    pass

class SingleIOCudaTask(SingleIOTask):
    pass
class MultipleIOCudaTask(MultipleIOTask):
    pass

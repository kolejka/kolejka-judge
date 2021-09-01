# vim:ts=4:sts=4:sw=4:expandtab


from kolejka.judge import config
from kolejka.judge.paths import *
from kolejka.judge.typing import *
from kolejka.judge.validators import *
from kolejka.judge.commands import *
from kolejka.judge.tasks.base import *
from kolejka.judge.tasks.check import *
from kolejka.judge.tasks.prepare import *
from kolejka.judge.tasks.run import *
from kolejka.judge.tasks.tools import *


__all__ = [ 'SingleIOTask', 'MultipleIOTask' ]
def __dir__():
    return __all__

class IOTask(TaskBase):
    DEFAULT_EXECUTABLE=config.SOLUTION_EXEC
    DEFAULT_ANSWER_PATH=config.TEST_ANSWER
    DEFAULT_GENERATOR_OUTPUT_PATH=config.TEST_INPUT
    DEFAULT_HINTER_OUTPUT_PATH=config.TEST_HINT
    DEFAULT_CASE_SENSITIVE=True
    DEFAULT_SPACE_SENSITIVE=False
    DEFAULT_TOOL_CPP_STANDARD=config.TOOL_BUILD_CPP_STANDARD
    @default_kwargs
    def __init__(self, executable, answer_path, generator_output_path, hinter_output_path, case_sensitive, space_sensitive, executable_arguments=None, input_path=None, hint_path=None, tool_override=None, tool_time=None, tool_cpp_standard=None, tool_libraries=None, generator_source=None, verifier_source=None, hinter_source=None, checker_source=None, limit_cores=1, limit_time=None, limit_cpu_time=None, limit_real_time=None, limit_memory=None, limit_gpu_memory=None, **kwargs):
        super().__init__(**kwargs)
        self.executable = executable
        self.executable_arguments = executable_arguments
        self.input_path = input_path
        self.hint_path = hint_path
        self.answer_path = answer_path
        self.tool_override = tool_override
        self.tool_time = tool_time
        self.tool_cpp_standard = tool_cpp_standard
        self.tool_libraries = tool_libraries
        self.generator_source = generator_source
        self.generator_output_path = generator_output_path
        self.verifier_source = verifier_source
        self.hinter_source = hinter_source
        self.hinter_output_path = hinter_output_path
        self.checker_source = checker_source
        self.limit_cores = limit_cores
        self.limit_cpu_time = limit_time
        self.limit_real_time = None
        if limit_time is not None:
            self.limit_real_time = parse_time(limit_time) + parse_time('1s')
        if limit_cpu_time is not None:
            self.limit_cpu_time = limit_cpu_time
        if limit_real_time is not None:
            self.limit_real_time = limit_real_time
        self.limit_memory = limit_memory
        self.limit_gpu_memory = limit_gpu_memory
        self.case_sensitive = case_sensitive
        self.space_sensitive = space_sensitive
        self.init_kwargs = kwargs


class SingleIOTask(IOTask):
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.steps = []

        input_path = self.input_path
        hint_path = self.hint_path
        answer_path = None
        if self.generator_source:
            generator = GeneratorTask(source=self.generator_source, output_path=self.generator_output_path, override=self.tool_override, input_path=input_path, limit_real_time=self.tool_time, cpp_standard=self.tool_cpp_standard, libraries=self.tool_libraries)
            input_path = generator.output_path
            self.steps.append(('generator', generator))
        if self.verifier_source:
            verifier = VerifierTask(source=self.verifier_source, override=self.tool_override, input_path=input_path, limit_real_time=self.tool_time, cpp_standard=self.tool_cpp_standard, libraries=self.tool_libraries)
            self.steps.append(('verifier', verifier))
        executor = self.solution_task_factory(executable=self.executable, executable_arguments=self.executable_arguments, input_path=input_path, answer_path=self.answer_path, limit_cores=self.limit_cores, limit_cpu_time=self.limit_cpu_time, limit_real_time=self.limit_real_time, limit_memory=self.limit_memory, limit_gpu_memory=self.limit_gpu_memory)
        answer_path = executor.answer_path
        self.steps.append(('executor', executor))
        if not hint_path and self.hinter_source:
            hinter_time=self.tool_time
            if hinter_time and self.limit_real_time and hinter_time < self.limit_real_time:
                hinter_time = self.limit_real_time
            hinter = HinterTask(source=self.hinter_source, output_path=self.hinter_output_path, override=self.tool_override, input_path=input_path, limit_real_time=hinter_time, cpp_standard=self.tool_cpp_standard, libraries=self.tool_libraries)
            hint_path = hinter.output_path
            self.steps.append(('hinter', hinter))
        if self.checker_source and input_path and hint_path and answer_path:
            checker = CheckerTask(source=self.checker_source, override=self.tool_override, input_path=input_path, hint_path=hint_path, answer_path=answer_path, limit_real_time=self.tool_time, cpp_standard=self.tool_cpp_standard, libraries=self.tool_libraries)
            self.steps.append(('checker', checker))
        else:
            if hint_path and answer_path:
                checker = AnswerHintDiffTask(hint_path=hint_path, answer_path=answer_path, case_sensitive=self.case_sensitive, space_sensitive=self.space_sensitive)
                self.steps.append(('checker', checker))

    def solution_task_factory(self, **kwargs):
        return SolutionExecutableTask(
            **kwargs
        )

    def set_system(self, system):
        super().set_system(system)
        for name, step in self.steps:
            step.set_system(system)

    def set_name(self, name):
        super().set_name(name)
        for step_name, step in self.steps:
            step.set_name(name+'_'+step_name)

    def execute(self):
        status = None
        for name, step in self.steps:
            step_result = step.execute()
            self.set_result(name=name, value=step_result)
            if step_result.status:
                status = step_result.status
                break
        self.set_result(status)
        return self.result


class MultipleIOTask(IOTask):
    @default_kwargs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alter_input_path(self, sub, input_path):
        return get_output_path(re.sub(sub[0], sub[1], str(input_path)))

    def create_single(self, input_path):
        test_name = re.sub(*config.MULTITEST_INPUT_NAME, str(input_path))
        test_dir = config.MULTITEST_SINGLE.format(test_name=test_name)
        self.run_command(self.name+'_'+test_name+'_prepare_dir', DirectoryAddCommand, path=test_dir, user_name=config.USER_TEST, group_name=config.USER_TEST)
        generator_output_path = config.MULTITEST_INPUT.format(test_name=test_name)
        hinter_output_path = config.MULTITEST_HINT.format(test_name=test_name)
        answer_path = config.MULTITEST_ANSWER.format(test_name=test_name)

        #TODO:Get values from files
        hint_path = list(self.find_files(self.alter_input_path(config.MULTITEST_INPUT_HINT, input_path)))
        if len(hint_path) > 1:
            #TODO: ?
            pass
        if hint_path:
            hint_path = hint_path[0]
        else:
            hint_path = None

        limit_cores = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_CORES, input_path))
        limit_cores = limit_cores and int(str(limit_cores, 'utf8').strip())
        if not limit_cores:
            limit_cores = self.limit_cores
        limit_time = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_TIME, input_path))
        limit_time = limit_time and parse_time(str(limit_time, 'utf8').strip())
        limit_cpu_time = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_CPU_TIME, input_path))
        limit_cpu_time = limit_cpu_time and parse_time(str(limit_cpu_time, 'utf8').strip())
        limit_cpu_time = limit_cpu_time or limit_time or self.limit_cpu_time
        limit_real_time = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_REAL_TIME, input_path))
        limit_real_time = limit_real_time and parse_time(str(limit_real_time, 'utf8').strip())
        limit_real_time = limit_real_time or limit_time and limit_time+parse_time('1s') or self.limit_real_time
        limit_memory = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_MEMORY, input_path))
        limit_memory = limit_memory and parse_memory(str(limit_memory, 'utf8').strip())
        limit_memory = limit_memory or self.limit_memory
        score = self.file_contents(self.alter_input_path(config.MULTITEST_INPUT_SCORE, input_path))
        score = score and float(str(score, 'utf8').strip())
        if score is None:
            score = 1.0

        single = SingleIOTask(
                executable=self.executable,
                executable_arguments=self.executable_arguments,
                input_path=input_path,
                hint_path=hint_path,
                answer_path=answer_path,
                tool_override=self.tool_override,
                tool_time=self.tool_time,
                generator_source=self.generator_source,
                generator_output_path=generator_output_path,
                verifier_source=self.verifier_source,
                hinter_source=self.hinter_source,
                hinter_output_path=hinter_output_path,
                checker_source=self.checker_source,
                limit_cores=limit_cores,
                limit_cpu_time=limit_cpu_time,
                limit_real_time=limit_real_time,
                limit_memory=limit_memory,
                case_sensitive=self.case_sensitive,
                space_sensitive=self.space_sensitive,
                **self.init_kwargs
            )
        single.set_name(self.name+'_'+test_name)
        single.set_system(self.system)
        return (test_name, single, score)

    def execute(self):
        prepare = PrepareTask(
                source=self.input_path,
                target=config.MULTITEST,
                allow_extract=True,
                user_name = config.USER_TEST,
                group_name = config.USER_TEST,
                result_on_error = 'INT'
                )
        prepare.set_name(self.name+'_prepare')
        prepare.set_system(self.system)
        status = None
        self.run_command(self.name+'_prepare_dir', DirectoryAddCommand, path=prepare.target, user_name=prepare.user_name, group_name=prepare.group_name)
        prepare_result = prepare.execute()
        if prepare_result.status:
            self.set_result(prepare_result.status, 'prepare', prepare_result)
        else:
            singles = []
            for path in self.find_files(prepare.target):
                if path.match(config.MULTITEST_INPUT_GLOB):
                    singles.append(self.create_single(path))
            singles = sorted(singles)

            score = 0.0
            max_score = 0.0
            for step_name, step, step_score in singles:
                step_result = step.execute()
                self.set_result(name='test_'+step_name, value=step_result)
                if not step_result.status:
                    step_result.set_status('OK')
                    score += step_score
                else:
                    if not status:
                        status = step_result.status
                max_score += step_score

            self.set_result(name='score', value=score)
            self.set_result(name='max_score', value=max_score)
            self.set_result(status)
        return self.result

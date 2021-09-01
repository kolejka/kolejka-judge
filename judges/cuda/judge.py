#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
import os, sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kolejka-judge'))
    from kolejka.judge import main
    main(__file__)
from kolejka.judge.commands import *
from kolejka.judge.parse import *
from kolejka.judge.tasks import *

def judge(args):
    tool_time = parse_time('60s')
    prepare_time = parse_time('5s')
    source_size_limit = parse_memory(args.test.get('source_size', '100K'))
    binary_size_limit = parse_memory(args.test.get('binary_size', '10M'))
    compile_time = parse_time(args.test.get('compile_time', '30s'))
    cpp_standard = args.test.get('cpp_standard', 'c++17')
    time_limit = parse_time(args.test.get('time', '10s'))
    memory_limit = parse_memory(args.test.get('memory', '1G'))
    time_gpu_limit = parse_time(args.test.get('time_gpu', '10s'))
    memory_gpu_limit = parse_memory(args.test.get('memory_gpu', '1G'))
    cuda_architecture = args.test.get('cuda_architecture', 'sm_52')
    cuda_profile = args.test.get('cuda_profile', '')
    args.add_steps(
        system=SystemPrepareTask(default_logs=False),
        source=SolutionPrepareTask(source=args.solution, allow_extract=True, override=args.test.get('environment', None), limit_real_time=prepare_time),
        source_rules=SolutionSourceRulesTask(max_size=source_size_limit),
        builder=SolutionBuildAutoTask([
            [SolutionBuildCMakeTask, [], {}],
            [SolutionBuildMakeTask, [], {}],
            [SolutionBuildNVCCTask, [], {'standard': cpp_standard, 'architecture': cuda_architecture}],
        ], limit_real_time=compile_time, limit_memory='2G'),
        build_rules=SolutionBuildRulesTask(max_size=binary_size_limit),
    )
    args.add_steps(io=SingleIOCudaTask(
        input_path=args.test.get('input', None),
        tool_override=args.test.get('tools', None),
        tool_time=tool_time,
        tool_cpp_standard=cpp_standard,
        generator_source=args.test.get('generator', None),
        verifier_source=args.test.get('verifier', None),
        hint_path=args.test.get('hint', None),
        hinter_source=args.test.get('hinter', None),
        checker_source=args.test.get('checker', None),
        limit_cores=1,
        limit_time=time_limit,
        limit_memory=memory_limit,
        limit_gpu_time=time_gpu_limit,
        limit_gpu_memory=memory_gpu_limit,
        cuda_metrics=["gpu__time_duration.sum"]
        )
    )
    args.add_steps(logs=CollectLogsTask())
    result = args.run()
    print('Result {} on test {}.'.format(result.status, args.id))

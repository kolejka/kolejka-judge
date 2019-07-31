#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'KolejkaJudge.zip'))
from kolejka.judge import *

args = parse_args(__file__)

results = ResultDict()

for test_id, test in args.tests.items():
    time_limit = parse_time(test.get('time', '10s'))
    one_second = parse_time('1s')
    memory_limit = parse_memory(test.get('memory', '1G'))
    checking = get_checking(args, test_id)
    checking.add_steps(
        prepare=SystemPrepareTask(default_logs=False),
        source=SolutionPrepareTask(source=args.solution, allow_extract=True, override=test.get('environment', None), limit_real_time='5s'),
        source_rules=SolutionSourceRulesTask(max_size='10K'),
        builder=SolutionBuildAutoTask([
            [SolutionBuildCMakeTask, [], {}],
            [SolutionBuildMakeTask, [], {}],
            [SolutionBuildGXXTask, [], {'standard': 'c++14',}],
        ], limit_real_time='30s', limit_memory='512M'),
        build_rules=SolutionBuildRulesTask(max_size='10M'),
    )
    input_path = test.get('input', None)
    hint_path = test.get('hint', None)
    tool_override = test.get('tools',None)
    if 'generator' in test:
        checking.add_steps(
            generator=GeneratorTask(source=test['generator'], override=tool_override, input_path=input_path, limit_real_time='10s')
        )
        input_path = checking.generator.output_path
    if 'verifier' in test:
        checking.add_steps(
            verifier=VerifierTask(source=test['verifier'], override=tool_override, input_path=input_path, limit_real_time='10s')
        )
    checking.add_steps(
        executor=SolutionExecutableTask(input_path=input_path, limit_cores=1, limit_cpu_time=time_limit, limit_real_time=time_limit+one_second, limit_memory=memory_limit)
    )
    if 'hinter' in test:
        checking.add_steps(
            hinter=HinterTask(source=test['hinter'], override=tool_override, input_path=input_path, limit_real_time=max(time_limit+one_second, parse_time('10s')))
        )
        hint_path = checking['hinter'].output_path
    if 'checker' in test:
        checking.add_steps(
            checker=CheckerTask(source=test['checker'], override=tool_override, input_path=input_path, hint_path=hint_path)
        )
    else:
        checking.add_steps(
            checker=AnswerHintDiffTask(hint_path=hint_path)
        )
    results.set(test_id, checking.run())
    print('Result {} on test {}.'.format(results[test_id].status, test_id))

write_results(args, results)

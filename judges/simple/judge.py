#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'KolejkaJudge.zip'))
from kolejka.judge import *

args = parse_args(__file__)

results = ResultDict()

for test_id, test in args.tests.items():
    time_limit = parse_time(test['time'])
    memory_limit = parse_memory(test['memory'])
    checking = get_checking(args, test_id)
    checking.add_steps(
        prepare=SystemPrepareTask(default_logs=False),
        source=SolutionPrepareTask(source=args.solution),
        source_rules=SolutionSourceRulesTask(max_size='10K'),
        builder=SolutionBuildGXXTask(standard='c++14'),
        build_rules=SolutionBuildRulesTask(max_size='10M'),
        executor=SolutionExecutableTask(
            input_path=test['input'],
            limit_cores=1,
            limit_cpu_time=time_limit,
            limit_real_time=time_limit*1.5,
            limit_memory=memory_limit
        ),
        checker=AnswerHintDiffTask(hint_path=test['hint']),
    )
    results.set(test_id, checking.run())
    print('Result {} on test {}.'.format(results[test_id].status, test_id))

write_results(args, results)

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
    time_limit = parse_time(args.test['time'])
    memory_limit = parse_memory(args.test['memory'])
    basename = args.test.get('basename', None)
    args.add_steps(
        prepare=SystemPrepareTask(default_logs=False),
        source=SolutionPrepareTask(source=args.solution, basename=basename),
        source_rules=SolutionSourceRulesTask(max_size='10K'),
        builder=SolutionBuildGXXTask(standard='c++17'),
        build_rules=SolutionBuildRulesTask(max_size='10M'),
        executor=SolutionExecutableTask(
            input_path=args.test['input'],
            limit_cores=1,
            limit_cpu_time=time_limit,
            limit_real_time=time_limit*1.5,
            limit_memory=memory_limit,
            limit_output_size=parse_memory('1G'),
            limit_error_size=parse_memory('1M'),
        ),
        checker=AnswerHintDiffTask(hint_path=args.test['hint']),
    )
    if parse_bool(args.test.get('debug', 'no')):
        args.add_steps(debug=CollectDebugTask())
    args.add_steps(
        logs=CollectLogsTask(),
    )
    result = args.run()
    print('Result {} on test {}.'.format(result.status, args.id))

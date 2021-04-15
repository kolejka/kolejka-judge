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
    time_limit = parse_time(args.test.get('time', '10s'))
    memory_limit = parse_memory(args.test.get('memory', '1G'))
    full_output = parse_bool(args.test.get('full_output', '0'))
    regex_count=[ rule.strip() for rule in args.test.get('regex_count', '').split('\n') if rule.strip() ],
    args.add_steps(
        system=SystemPrepareTask(default_logs=False),
        postgres=PostgresPrepareTask(default_logs=True),
        source=SolutionPrepareTask(source=args.solution, allow_extract=True, limit_real_time=prepare_time),
        source_rules=SolutionSourceRulesTask(max_size=source_size_limit),
    )
    args.add_steps(io=SingleBuildIOPostgresTask(
        task=args.test.get('task', None),
        tool_time=tool_time,
        tuples_only=not full_output,
        align=full_output,
        regex_count=regex_count,
        generator_source=args.test.get('generator', None),
        hint_path=args.test.get('hint', None),
        hinter_source=args.test.get('hinter', None),
        checker_source=args.test.get('checker', None),
        checker_ignore_errors=parse_bool(args.test.get('checker_ignore_errors', '0')),
        limit_cores=1,
        limit_time=time_limit,
        limit_memory=memory_limit,
        ignore_errors=parse_bool(args.test.get('ignore_errors', '0')),
        row_sort=args.test.get('row_sort', None),
        column_sort=args.test.get('column_sort', None),
    ))
    args.add_steps(background=ClearBackgroundTask())
    args.add_steps(logs=CollectLogsTask())
    result = args.run()
    print('Result {} on test {}.'.format(result.status, args.id))

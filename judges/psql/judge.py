#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab
import os, re, sys
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
    basename = args.test.get('basename', None)
    full_output = parse_bool(args.test.get('full_output', '0'))
    regex_count=[ rule.strip() for rule in args.test.get('regex_count', '').split('\n') if rule.strip() ]
    task = args.test.get('task', None)
    task = task and str(task) or None
    args.add_steps(
        system=SystemPrepareTask(default_logs=False),
        source=SolutionPrepareTask(source=args.solution, basename=basename, allow_extract=True, limit_real_time=prepare_time),
    )
    if task is not None:
        source_regex=r'^\s*--'+re.escape(task)+r'\s*$.*^\s*----\s*$>0'
        args.add_steps(
            task_rules=SolutionSourceRulesTask(regex_count=source_regex, result_on_error='TSK'),
        )
    args.add_steps(
        source_rules=SolutionSourceRulesTask(max_size=source_size_limit),
        postgres=PostgresPrepareTask(default_logs=True),
    )
    args.add_steps(io=SingleBuildIOPostgresTask(
        task=task,
        task_required=True,
        score=parse_memory(args.test.get('score', '1')),
        tool_time=tool_time,
        tuples_only=not full_output,
        align=full_output,
        regex_count=regex_count,
        generator_source=args.test.get('generator', None),
        finalizer_source=args.test.get('finalizer', None),
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
    if parse_bool(args.test.get('debug', 'no')):
        args.add_steps(debug=CollectDebugTask())
    args.add_steps(logs=CollectLogsTask())
    result = args.run()
    print('Result {} on test {}.'.format(result.status, args.id))

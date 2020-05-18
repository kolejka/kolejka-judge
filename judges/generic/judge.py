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
    time_limit = parse_time(args.test.get('time', '10s'))
    one_second = parse_time('1s')
    memory_limit = parse_memory(args.test.get('memory', '1G'))
    args.add_steps(
        prepare=SystemPrepareTask(default_logs=False),
        source=SolutionPrepareTask(source=args.solution, allow_extract=True, override=args.test.get('environment', None), limit_real_time='5s'),
        source_rules=SolutionSourceRulesTask(max_size='10K'),
        builder=SolutionBuildAutoTask([
            [SolutionBuildCMakeTask, [], {}],
            [SolutionBuildMakeTask, [], {}],
            [SolutionBuildGXXTask, [], {'standard': 'c++14',}],
        ], limit_real_time='30s', limit_memory='512M'),
        build_rules=SolutionBuildRulesTask(max_size='10M'),
    )
    input_path = args.test.get('input', None)
    hint_path = args.test.get('hint', None)
    tool_override = args.test.get('tools',None)
    if 'generator' in args.test:
        args.add_steps(
            generator=GeneratorTask(source=args.test['generator'], override=tool_override, input_path=input_path, limit_real_time='10s')
        )
        input_path = args.generator.output_path
    if 'verifier' in args.test:
        args.add_steps(
            verifier=VerifierTask(source=args.test['verifier'], override=tool_override, input_path=input_path, limit_real_time='10s')
        )
    args.add_steps(
        executor=SolutionExecutableTask(input_path=input_path, limit_cores=1, limit_cpu_time=time_limit, limit_real_time=time_limit+one_second, limit_memory=memory_limit)
    )
    if 'hinter' in args.test:
        args.add_steps(
            hinter=HinterTask(source=args.test['hinter'], override=tool_override, input_path=input_path, limit_real_time=max(time_limit+one_second, parse_time('10s')))
        )
        hint_path = args.hinter.output_path
    if 'checker' in args.test:
        args.add_steps(
            checker=CheckerTask(source=args.test['checker'], override=tool_override, input_path=input_path, hint_path=hint_path)
        )
    else:
        args.add_steps(
            checker=AnswerHintDiffTask(hint_path=hint_path)
        )
    args.add_steps(logs=CollectLogsTask())
    result = args.run()
    print('Result {} on test {}.'.format(result.status, args.id))

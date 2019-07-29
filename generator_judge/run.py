#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

KOLEJKA_JUDGE_LIBRARY='KolejkaJudge.zip'
from pathlib import Path
import sys
library = Path(__file__).parent.resolve()/KOLEJKA_JUDGE_LIBRARY
if library.is_file():
    sys.path.insert(0, str(library))

import kolejka.judge
from kolejka.judge.commands import *
from kolejka.judge.limits import *
from kolejka.judge.parse import *
from kolejka.judge.paths import *
from kolejka.judge.tasks import *

args = kolejka.judge.parse_args()
results = dict()

for test_id, test in args.tests.items():
    checking = kolejka.judge.Checking(system=args.system(output_directory = args.output_directory / str(test_id), paths=args.input_paths[test_id]))
    checking.system.add_path(args.solution)
    checking.add_steps(
        prepare=SystemPrepareTask(default_logs=True),
        source=SolutionPrepareTask(source=get_input_path(args.solution), allow_extract=True, override=test.get('environment', None), limit_real_time='5s'),
        source_rules=SolutionSourceRulesTask(max_size='10K'),
        builder=SolutionBuildAutoTask([
            [SolutionBuildCMakeTask, [], {}],
            [SolutionBuildMakeTask, [], {}],
            [SolutionBuildGXXTask, [], {'standard': 'c++14',}],
        ], limit_real_time='30s', limit_memory='256M'),
        build_rules=SolutionBuildRulesTask(max_size='10M'),
    )
    input_path = get_input_path(test.get('input', None))
    hint_path = get_input_path(test.get('hint', None))
    tool_override = get_input_path(test.get('tools',None))
    if 'generator' in test:
        checking.add_steps(
            generator=GeneratorTask(source=get_input_path(test['generator']), override=tool_override, input_path=input_path, limit_real_time='10s')
        )
        input_path = checking.generator.output_path
    if 'verifier' in test:
        checking.add_steps(
            verifier=VerifierTask(source=get_input_path(test['verifier']), override=tool_override, input_path=input_path, limit_real_time='10s')
        )
    time_limit = parse_time(test.get('time', '10s'))
    one_second = parse_time('1s')
    memory_limit = test.get('memory', '1G')
    checking.add_steps(
        executor=SolutionExecutableTask(executable=checking.builder.execution_script, input_path=input_path, limit_cores=1, limit_cpu_time=time_limit, limit_real_time=time_limit+one_second, limit_memory=memory_limit)
    )
    answer_path = checking.executor.answer_path
    if 'hinter' in test:
        checking.add_steps(
            hinter=HinterTask(source=get_input_path(test['hinter']), override=tool_override, input_path=input_path, limit_real_time=max(time_limit+one_second, parse_time('10s')))
        )
        hint_path = checking['hinter'].output_path
    if 'checker' in test:
        checking.add_steps(
            checker=CheckerTask(source=get_input_path(test['checker']), override=tool_override, input_path=input_path, hint_path=hint_path, answer_path=answer_path)
        )
    else:
        checking.add_steps(
            checker=AnswerHintDiffTask(hint_path=hint_path, answer_path=answer_path)
        )
    status, res = checking.run()
    results[test_id] = res
    print(test_id, status)

print(results)
kolejka.judge.write_results(args, results)

#!/usr/bin/env python3

KOLEJKA_JUDGE_LIBRARY='KolejkaJudge.zip'

import json
import os
from pathlib import Path
import sys

library = Path(__file__).parent/KOLEJKA_JUDGE_LIBRARY
if library.is_file():
    sys.path.insert(0, str(library))

from kolejka.judge.checking import Checking

import judge
args = judge.parse_args()

results = dict()

for test_id, test in args.tests.items():
    print(test)
    solution_path = args.solution.resolve()
    solution_override=None
    if 'environment' in test:
        solution_override = Path(test['environment'].path).resolve()
    test_override=None
    if 'tools' in test:
        test_override = Path(test['tools'].path).resolve()
    checking = Checking(environment=args.environment(args.output_dir / str(test_id)))
    checking.add_steps(prepare=judge.SatoriSystemPrepareTask())
    checking.add_steps(source=judge.SatoriSolutionPrepareTask(solution_path, override=solution_override))
    checking.add_steps(build=judge.SatoriSolutionBuildTask())
    input_path = '/dev/null'
    if 'input' in test:
        input_path = Path(test['input'].path).resolve()
    if 'generator' in test:
        generator_path = Path(test['generator'].path).resolve()
        checking.add_steps(generator_source=judge.SatoriToolPrepareTask('generator', generator_path, override=test_override))
        checking.add_steps(generator_build=judge.SatoriToolBuildTask('generator'))
        generator_output = 'test/input'
        checking.add_steps(generator_run=judge.SatoriToolRunTask('generator', stdin=input_path, stdout=generator_output))
        input_path = generator_output
    if 'verifier' in test:
        verifier_path = Path(test['verifier'].path).resolve()
        checking.add_steps(verifier_source=judge.SatoriToolPrepareTask('verifier', verifier_path, override=test_override))
        checking.add_steps(verifier_build=judge.SatoriToolBuildTask('verifier'))
        checking.add_steps(verifier_run=judge.SatoriToolRunTask('verifier', stdin=input_path))
    output_path = 'test/output'
    checking.add_steps(run=judge.SatoriSolutionRunTask(stdin=input_path, stdout=output_path))
    hint_path = input_path
    if 'hint' in test:
        hint_path = Path(test['hint'].path).resolve()
    if 'hinter' in test:
        hinter_path = Path(test['hinter'].path).resolve()
        checking.add_steps(hinter_source=judge.SatoriToolPrepareTask('hinter', hinter_path, override=test_override))
        checking.add_steps(hinter_build=judge.SatoriToolBuildTask('hinter'))
        hinter_output = 'test/hint'
        checking.add_steps(hinter_run=judge.SatoriToolRunTask('hinter', stdin=hint_path, stdout=hinter_output))
        hint_path = hinter_output
    if 'checker' in test:
        checker_path = Path(test['checker'].path).resolve()
        checking.add_steps(checker_source=judge.SatoriToolPrepareTask('checker', checker_path, override=test_override))
        checking.add_steps(checker_build=judge.SatoriToolBuildTask('checker'))
        checking.add_steps(checker_run=judge.SatoriToolRunTask('checker', cmdline_options=[input_path, hint_path, output_path]))
    else:
        checking.add_steps(checker=judge.SatoriDiff(output_path, hint_path))

    status, res = checking.run()
    
    print(json.dumps(checking.format_result(res), indent=4))
    print(status)
    
    results[test_id] = res

judge.write_results(args, results)

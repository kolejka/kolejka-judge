# vim:ts=4:sts=4:sw=4:expandtab
import pathlib
import subprocess
import tempfile

def judge_parser(parser):
    parser.add_argument('--update', action='store_true', default=False, help='Update Kolejka Judge library')
    parser.add_argument('--task', type=str, help='Task folder')
    parser.add_argument('--client', action='store_true', default=False, help='Run using Kolejka Client')
    parser.add_argument('--judge', required=True, type=str, help='Judge script')
    parser.add_argument('--tests', type=str, help='Tests description')
    parser.add_argument('--solution', type=str, help='Solution file')
    parser.add_argument('--output-directory', type=str, help='Output directory')
    def execute(args):
        from kolejka.judge.ctxyaml import ctxyaml_load
        from kolejka.judge.task import kolejka_task
        from kolejka.judge.update import kolejka_update

        if sum([ 1 if action else 0 for action in [ args.update, args.task, args.client ] ]) != 1:
            parser.error("Please specify exactly one action: update, task, or client")
        
        if args.update:
            kolejka_update(args.judge)
            return
        
        if not args.tests:
            parser.error("the following arguments are required: --tests")
        if not args.solution:
            parser.error("the following arguments are required: --solution")

        tests = dict()
        if not pathlib.Path(args.tests).is_file():
            parser.error('TESTS file {} does not exist'.format(args.tests))
        try:
            tests = dict([ (str(k),v) for k,v in ctxyaml_load(args.tests).items() ])
        except:
            parser.error('TESTS file {} is invalid'.format(args.tests))

        if args.task:
            kolejka_task(args.task, tests, args.solution, args.judge)
            return 

        if args.client:
            if not args.output_directory:
                parser.error("the following arguments are required: --output-directory")
            with tempfile.TemporaryDirectory() as temp_dir:
                kolejka_task(temp_dir, tests, args.solution, args.judge, exist_ok=True)
                subprocess.run(['kolejka-client', 'execute', temp_dir, args.output_directory], check=True)
            return
    parser.set_defaults(execute=execute)

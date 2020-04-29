# vim:ts=4:sts=4:sw=4:expandtab

def judge_parser(parser):
    parser.add_argument('--update', action='store_true', default=False, help='Update Kolejka Judge library')
    parser.add_argument('--task', type=str, help='Task folder')
    parser.add_argument('--client', action='store_true', default=False, help='Run using Kolejka Client')
    parser.add_argument('--judge', required=True, type=str, help='Judge script')
    parser.add_argument('--tests', required=True, type=str, help='Tests description')
    parser.add_argument('--solution', required=True, type=str, help='Solution file')
    parser.add_argument('--output-directory', default='results', type=str, help='Output directory')
    def execute(args):
        if args.update:
            from kolejka.judge.update import kolejka_update
            kolejka_update(args.judge)
            return

        tests = dict()
        import logging
        import pathlib
        if not pathlib.Path(args.tests).is_file():
            logging.error('TESTS file {} does not exist'.format(args.tests))
        try:
            tests = dict([ (str(k),v) for k,v in ctxyaml_load(args.tests).items() ])
        except:
            logging.error('Failed to load TESTS file {}'.format(args.tests))

        if args.task:
            from kolejka.judge.task import kolejka_task
            kolejka_task(args.task, tests, args.solution, args.judge)
            return 

        if args.client:
            from kolejka.judge.task import kolejka_task
            with tempfile.TemporaryDirectory() as temp_dir:
                kolejka_task(temp_dir, tests, args.solution, args.judge, exist_ok=True)
                subprocess.run(['kolejka-client', 'execute', temp_dir, args.output_directory], check=True)
            return
    parser.set_defaults(execute=execute)


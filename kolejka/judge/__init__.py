# vim:ts=4:sts=4:sw=4:expandtab


def main(judge_path=None):
    import argparse
    import logging
    import setproctitle
    from kolejka.judge.judge import config_parser as judge_parser

    setproctitle.setproctitle('kolejka-judge')
    parser = argparse.ArgumentParser(description='KOLEJKA judge')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show more info')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='show debug info')
    judge_parser(parser, judge_path=judge_path)
    args = parser.parse_args()
    level=logging.WARNING
    if args.verbose:
        level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    logging.basicConfig(level = level)
    args.execute(args)


if __name__ == '__main__':
    main()

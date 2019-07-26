# vim:ts=4:sts=4:sw=4:expandtab
import argparse
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge.systems import *


KNOWN_SYSTEMS = {
    'local': LocalSystem,
    'kolejkaobserver': ObserverSystem,
    'psutil': PsutilSystem,
}


def parse_default_arguments(command):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', dest='output_directory')
    return vars(parser.parse_known_args(command)[0])


KNOWN_SYSTEMS_ARGUMENTS = {
    'local': parse_default_arguments,
    'kolejkaobserver': parse_default_arguments,
    'psutil': parse_default_arguments,
}


def detect_system():
    default_system = 'local'

    parser = argparse.ArgumentParser()

    for sys_id, sys_cls in KNOWN_SYSTEMS.items():
        parser.add_argument(
            '--{}'.format(sys_id),
            dest='system',
            action='store_const',
            const=sys_id,
            default=default_system,
        )

    args, remnants = parser.parse_known_args()
    system_arguments = KNOWN_SYSTEMS_ARGUMENTS[args.system](remnants)
    return KNOWN_SYSTEMS[args.system](**system_arguments)

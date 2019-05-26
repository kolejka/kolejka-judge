import argparse
import json

from environments import LocalComputer, KolejkaObserver, PsutilEnvironment, KolejkaTask

KNOWN_ENVIRONMENTS = {
    'local': LocalComputer,
    'kolejkaobserver': KolejkaObserver,
    'psutil': PsutilEnvironment,
    'kolejkatask': KolejkaTask,
}


def parse_kolejkatask_arguments(command):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', dest='output_directory')
    parser.add_argument('--image', dest='image')
    parser.add_argument('--files', dest='files', nargs='*')
    parser.add_argument('--environment', dest='environment', type=json.loads)
    parser.add_argument('--requires', dest='requires')
    parser.add_argument('--exclusive', dest='exclusive')
    parser.add_argument('--limits', dest='limits')
    parser.add_argument('--collect', dest='collect')
    parser.add_argument('--config', dest='config')
    return vars(parser.parse_known_args(command)[0])


def parse_default_arguments(command):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', dest='output_directory')
    return vars(parser.parse_known_args(command)[0])


KNOWN_ENVIRONMENTS_ARGUMENTS = {
    'local': parse_default_arguments,
    'kolejkaobserver': parse_default_arguments,
    'psutil': parse_default_arguments,
    'kolejkatask': parse_kolejkatask_arguments,
}


def detect_environment():
    default_environment = 'local'

    parser = argparse.ArgumentParser()

    for env_id, env_cls in KNOWN_ENVIRONMENTS.items():
        parser.add_argument(
            '--{}'.format(env_id),
            dest='environment',
            action='store_const',
            const=env_id,
            default=default_environment,
        )

    args, remnants = parser.parse_known_args()
    environment_arguments = KNOWN_ENVIRONMENTS_ARGUMENTS[args.environment](remnants)
    return KNOWN_ENVIRONMENTS[args.environment](**environment_arguments)

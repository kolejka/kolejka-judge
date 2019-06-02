import argparse

from kolejka.judge.environments import LocalComputer, KolejkaObserver, PsutilEnvironment

KNOWN_ENVIRONMENTS = {
    'local': LocalComputer,
    'kolejkaobserver': KolejkaObserver,
    'psutil': PsutilEnvironment,
}


def parse_default_arguments(command):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', dest='output_directory')
    return vars(parser.parse_known_args(command)[0])


KNOWN_ENVIRONMENTS_ARGUMENTS = {
    'local': parse_default_arguments,
    'kolejkaobserver': parse_default_arguments,
    'psutil': parse_default_arguments,
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

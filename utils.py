import argparse

from environments import LocalComputer, KolejkaObserver


def detect_environment():
    known_environments = {
        'local': LocalComputer,
        'kolejka': KolejkaObserver,
    }
    default_environment = 'local'

    parser = argparse.ArgumentParser()

    for env_id, env_cls in known_environments.items():
        parser.add_argument(
            '--{}'.format(env_id),
            dest='environment',
            action='store_const',
            const=env_id,
            default=default_environment,
        )

    args = parser.parse_args()
    return known_environments[args.environment]()

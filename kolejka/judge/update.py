# vim:ts=4:sts=4:sw=4:expandtab
import logging
import pathlib
import urllib


from kolejka.judge import config


__all__ = [ 'kolejka_update', ]
def __dir__():
    return __all__


def kolejka_update(judgepy):
    with urllib.request.urlopen(config.DISTRIBUTION_ADDRESS) as library_request:
        if library_request.status == 200 and library_request.reason == 'OK':
            library_data = library_request.read()
            library_path = pathlib.Path(judgepy).resolve().parent / config.DISTRIBUTION_PATH
            with library_path.open('wb') as library_file:
                library_file.write(library_data)
            logging.warning('New Kolejka Judge library installed')

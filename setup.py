#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab

import re
import os
import setuptools

def sub_find_packages(module):
    return [ module ] + [ module + '.' + submodule for submodule in setuptools.find_packages(re.sub(r'\.', r'/', module)) ]

kolejka_judge = {
        'name' : 'KolejkaJudge',
        'description' : 'Kolejka Satori Judge',
        'packages' : sub_find_packages('kolejka.judge'),
        'url' : 'https://github.com/kolejka/kolejka-judge',
        'install_requires' : [
            'appdirs',
            'setproctitle',
        ],
        'author' : 'KOLEJKA',
        'author_email' : 'kolejka@matinf.uj.edu.pl',
        'long_description' : 'kolejka is a lightweight task scheduling platform developed for a small computational grid at Faculty of Mathematics and Computer Science of the Jagiellonian University in Kraków.',
        'license' : 'MIT',
        'version' : '0.1',
        'python_requires' : '>=3.6',
        'namespace_packages' : [ 'kolejka' ],
    }

if __name__ == '__main__':
    import datetime
    import subprocess
    import sys
    p = subprocess.Popen(['git', 'show', '-s', '--format=%at'], stdout=subprocess.PIPE)
    s = datetime.datetime.fromtimestamp(int(p.communicate()[0]), datetime.timezone.utc)
    assert p.returncode == 0
    kolejka_judge['version'] += '.'+s.strftime('%Y%m%d%H%M')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup.cfg'), 'w') as setup_cfg:
        setup = list()
        setup.append('[metadata]')
        for key in [ 'name', 'version', 'url', 'download_url', 'author', 'author_email', 'maintainer', 'maintainer_email', 'classifiers', 'license', 'description', 'long_description', 'long_description_content_type', 'keywords', 'platforms', 'provides', 'requires', 'obsoletes' ]:
            if key in kolejka_judge:
                val = kolejka_judge[key]
                if isinstance(val, list):
                    val = ', '.join(val)
                setup.append('{} = {}'.format(key, val))
        setup.append('[options]')
        for key in [ 'namespace_packages', 'python_requires' ]:
            if key in kolejka_judge:
                val = kolejka_judge[key]
                if isinstance(val, list):
                    val = ', '.join(val)
                setup.append('{} = {}'.format(key, val))
        setup_cfg.writelines([line+'\n' for line in setup])
    setuptools.setup(**kolejka_judge)

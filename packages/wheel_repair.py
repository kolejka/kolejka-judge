#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab


import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import venv


parser = argparse.ArgumentParser()
parser.add_argument('wheel', type=Path, help='Wheel to repair')
parser.add_argument('result', type=Path, help='Result')
args = parser.parse_args()

pip_deps = [ 'KolejkaCommon', 'KolejkaClient', 'KolejkaObserver' ]

args.wheel = args.wheel.resolve()
args.result = args.result.resolve()
assert args.wheel.is_file()
with tempfile.TemporaryDirectory() as work_dir:
    wheel_dir = Path(work_dir) / 'wheel'
    wheel_dir.mkdir()
    subprocess.run(['unzip', str(args.wheel)], cwd=wheel_dir, check=True)
    pip_dir = Path(work_dir) / 'pip'
    pip_dir.mkdir()
    for pip_dep in pip_deps:
        subprocess.run(['pip3', 'download', pip_dep], cwd=pip_dir, check=True)
        whl = sorted(pip_dir.glob(pip_dep+'*.whl'))[-1]
        subprocess.run(['unzip', str(whl)], cwd=pip_dir, check=True)
    subprocess.run(['rsync', '-a', str(pip_dir / 'kolejka'), './'], cwd=wheel_dir, check=True)

    with ( wheel_dir / '__main__.py' ).open('w') as main_file:
        main_file.write('''
if __name__ == '__main__':
    from kolejka.judge import main
    main()
''')
    first = Path(work_dir) / 'first.zip'
    subprocess.run(['zip', '-9', str(first), '-r', '.'], cwd=wheel_dir, check=True)
    second = Path(work_dir) / 'second.zip'
    with second.open('wb') as second_file:
        second_file.write(bytes('#!/usr/bin/env python3\n', 'utf8'))
        with first.open('rb') as first_file:
            second_file.write(first_file.read())
    shutil.move(second, args.result)
    args.result.chmod(0o755)

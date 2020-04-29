#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab


import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


parser = argparse.ArgumentParser()
parser.add_argument('wheel', nargs='+', help='Wheel to repair')
args = parser.parse_args()

for wheel in args.wheel:
    wheel = Path(wheel).resolve()
    assert wheel.is_file()
    with tempfile.TemporaryDirectory() as work_dir:
        subprocess.run(['unzip', str(wheel)], cwd=work_dir, check=True)
        with ( Path(work_dir) / '__main__.py' ).open('w') as main_file:
            main_file.write('''
if __name__ == '__main__':
    from kolejka.judge import main
    main()
''')
        with tempfile.TemporaryDirectory() as zip_dir:
            first = Path(zip_dir) / 'first.zip'
            subprocess.run(['zip', '-9', str(first), '-r', '.'], cwd=work_dir, check=True)
            second = Path(zip_dir) / 'second.zip'
            with second.open('wb') as second_file:
                second_file.write(bytes('#!/usr/bin/env python3\n', 'utf8'))
                with first.open('rb') as first_file:
                    second_file.write(first_file.read())
            shutil.move(second, wheel)

#!/usr/bin/env python3
# vim:ts=4:sts=4:sw=4:expandtab


import argparse
from pathlib import Path
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
        subprocess.run(['zip', '-9', str(wheel), '-r', '.'], cwd=work_dir, check=True)

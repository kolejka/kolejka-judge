#!/bin/bash
. prepare.sh

pushd "${JUDGE}" >/dev/null 2>&1
    rm -rf TASK
    ./judge.py "$@" --task TASK
popd >/dev/null 2>&1

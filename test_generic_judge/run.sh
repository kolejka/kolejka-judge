#!/bin/bash
. prepare.sh

pushd "${JUDGE}" >/dev/null 2>&1
    rm -rf RESULT
    ./judge.py execute tests/tests.yaml solution/* RESULT
popd >/dev/null 2>&1

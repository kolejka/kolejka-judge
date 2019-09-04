#!/bin/bash
. prepare.sh

pushd "${JUDGE}" >/dev/null 2>&1
    rm -rf TASK
    ./judge.py "$@" --task TASK
    rm -rf RESULT-CLIENT
    kolejka-client execute TASK RESULT-CLIENT
popd >/dev/null 2>&1

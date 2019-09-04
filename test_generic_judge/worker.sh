#!/bin/bash
. prepare.sh

pushd "${JUDGE}" >/dev/null 2>&1
    rm -rf TASK
    ./judge.py "$@" --task TASK
    rm -rf /tmp/TASK
    rsync -a TASK /tmp
    rm -rf RESULT-WORKER-STAGE2
    rm -rf /tmp/RESULT-WORKER-STAGE2
    mkdir -p /tmp/RESULT-WORKER-STAGE2
    kolejka-worker stage2 /tmp/TASK /tmp/RESULT-WORKER-STAGE2
    rsync -a /tmp/RESULT-WORKER-STAGE2 .
    rm -rf RESULT-WORKER-EXECUTE
    rm -rf /tmp/RESULT-WORKER-EXECUTE
    kolejka-worker execute /tmp/TASK /tmp/RESULT-WORKER-EXECUTE
    rsync -a /tmp/RESULT-WORKER-EXECUTE .
popd >/dev/null 2>&1

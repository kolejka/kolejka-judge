#!/bin/bash
. prepare.sh

pushd "${OFFICE}" >/dev/null 2>&1
    for TD in $(ls -1 "${JUDGE}/tests"); do
        echo " === ${TD} === "
        rm -rf "${TD}_task"
        "${JUDGE}/judge.py" task "${JUDGE}/tests/${TD}/tests/tests.yaml" "${JUDGE}/tests/${TD}/solution/"* "${TD}_task"
    done
popd >/dev/null 2>&1

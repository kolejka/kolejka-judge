#!/bin/bash
. prepare.sh

pushd "${OFFICE}" >/dev/null 2>&1
    for TD in $(ls -1 "${JUDGE}/tests"); do
        echo " === ${TD} === "
        rm -rf "${TD}_result_execute"
        "${JUDGE}/judge.py" execute "${JUDGE}/tests/${TD}/tests/tests.yaml" "${JUDGE}/tests/${TD}/solution/"* "${TD}_result_execute" "$@"
    done
popd >/dev/null 2>&1

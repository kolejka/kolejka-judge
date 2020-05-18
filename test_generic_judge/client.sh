#!/bin/bash
. prepare.sh

pushd "${OFFICE}" >/dev/null 2>&1
    for TD in $(ls -1 "${JUDGE}/tests"); do
        echo " === ${TD} === "
        rm -rf "${TD}_task_client"
        "${JUDGE}/judge.py" task "${JUDGE}/tests/${TD}/tests/tests.yaml" "${JUDGE}/tests/${TD}/solution/"* "${TD}_task_client"
        rm -rf "${TD}_result_client"
        kolejka-client execute "${TD}_task_client" "${TD}_result_client"
    done
popd >/dev/null 2>&1

#!/bin/bash
. prepare.sh

pushd "${OFFICE}" >/dev/null 2>&1
    for TD in $(ls -1 "${JUDGE}/tests"); do
        echo " === ${TD} === "
        rm -rf "${TD}_task_worker"
        "${JUDGE}/judge.py" task "${JUDGE}/tests/${TD}/tests/tests.yaml" "${JUDGE}/tests/${TD}/solution/"* "${TD}_task_worker"
        TT="$(mktemp -d)"
        rsync -a "${TD}_task_worker/" "${TT}/"
        find "${TT}" -type l -xtype f |while read link; do
            real=$(readlink -f "${link}")
            rm "${link}"
            rsync -a "${real}" "${link}"
        done

        rm -rf "${TD}_result_worker_stage2"
        mkdir -p "${TD}_result_worker_stage2"
        TR="$(mktemp -d)"
        kolejka-worker stage2 "${TT}" "${TR}" "$@"
        rsync -a "${TR}/" "${TD}_result_worker_stage2/" 
        rm -rf "${TR}"

        rm -rf "${TD}_result_worker_stage0"
        mkdir -p "${TD}_result_worker_stage0"
        TR="$(mktemp -d)"
        kolejka-worker execute "${TT}" "${TR}" "$@"
        rsync -a "${TR}/" "${TD}_result_worker_stage0/" 
        rm -rf "${TR}"

        rm -rf "${TT}"
    done
popd >/dev/null 2>&1

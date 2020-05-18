#!/bin/bash
. prepare.sh

pushd "${JUDGE}" >/dev/null 2>&1
    pushd "${KOLEJKA}/packages/KolejkaJudge" >/dev/null 2>&1
        rm -rf dist
        python3 setup.py bdist_wheel >/dev/null 2>&1
        BUILD="$(ls -1 dist/KolejkaJudge-*-py3-none-any.whl |tail -n 1)"
        if [ -f "${BUILD}" ]; then
            python3 "${KOLEJKA}/packages/wheel_repair.py" "${BUILD}" "${JUDGE}/${LIBRARY}" >/dev/null 2>&1
        else
            rm "${JUDGE}/${LIBRARY}" 
        fi
    popd >/dev/null 2>&1
popd >/dev/null 2>&1

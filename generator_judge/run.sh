#!/bin/bash
LIBRARY="KolejkaJudge.zip"
OFFICE="$(readlink -f "$(dirname "$(which "$0")")")"

pushd "${OFFICE}" >/dev/null 2>&1
    rm -rf "${LIBRARY}" 

    pushd ".." >/dev/null 2>&1
        rm -rf dist
        python3 setup.py bdist_wheel >/dev/null 2>&1
        BUILD="$(ls -1 dist/KolejkaJudge-*-py3-none-any.whl |tail -n 1)"
        cp -a "${BUILD}" "${OFFICE}/${LIBRARY}"
        python3 wheel_repair.py "${OFFICE}/${LIBRARY}" >/dev/null 2>&1
    popd >/dev/null 2>&1

    rm -rf results

    ./run.py "$@"

popd >/dev/null 2>&1

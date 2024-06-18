#!/bin/bash
OFFICE="$(readlink -f "$(dirname "$(which "$0")")")"
JUDGEPY="$(readlink -f "${OFFICE}/../judge.py")"
TESTS="${1:-$(ls -1 "${OFFICE}")}"
EXECUTE="execute"

for TD in ${TESTS}; do
    if [ -f "${OFFICE}/${TD}/tests/tests.yaml" ]; then
        echo " === ${TD} === "
        if [ -f "${OFFICE}/${TD}/tests/Makefile" ]; then
            make -C "${OFFICE}/${TD}/tests" -f Makefile
        fi
        for SOL in $(ls -1 "${OFFICE}/${TD}/solutions"); do
            if [ -f "${OFFICE}/${TD}/solutions/${SOL}" ]; then
                echo "  + ${SOL}"
                mkdir -p "${OFFICE}/results"
                rm -rf "${OFFICE}/results/${TD}_${SOL}_${EXECUTE}"
                "${JUDGEPY}" ${EXECUTE} "${OFFICE}/${TD}/tests/tests.yaml" "${OFFICE}/${TD}/solutions/${SOL}" "${OFFICE}/results/${TD}_${SOL}_${EXECUTE}"
                if [ -f "${OFFICE}/results/${TD}_${SOL}_${EXECUTE}/results.yaml" ]; then
                    if [ -x "${OFFICE}/${TD}/check_result" ]; then
                        if "${OFFICE}/${TD}/check_result" "${OFFICE}/results/${TD}_${SOL}_${EXECUTE}/results.yaml"; then
                            true
                        else
                            echo "   TEST !!! CHECK FAIL !!!"
                        fi
                    fi
                else
                    echo "   TEST !!! NO RESULT FAIL !!!"
                fi
            fi
        done
    fi
done

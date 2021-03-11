#!/bin/bash
OFFICE="$(readlink -f "$(dirname "$(which "$0")")")"
JUDGEPY="$(readlink -f "${OFFICE}/../judge.py")"

for TD in $(ls -1 "${OFFICE}"); do
    if [ -f "${OFFICE}/${TD}/tests/tests.yaml" ]; then
        echo " === ${TD} === "
        for SOL in $(ls -1 "${OFFICE}/${TD}/solutions"); do
            if [ -f "${OFFICE}/${TD}/solutions/${SOL}" ]; then
                echo "  + ${SOL}"
                mkdir -p "${OFFICE}/results"
                rm -rf "${OFFICE}/results/${TD}_${SOL}_execute"
                "${JUDGEPY}" execute "$@" "${OFFICE}/${TD}/tests/tests.yaml" "${OFFICE}/${TD}/solutions/${SOL}" "${OFFICE}/results/${TD}_${SOL}_execute" "$@"
                if [ -f "${OFFICE}/results/${TD}_${SOL}_execute/results.yaml" ]; then
                    if [ -x "${OFFICE}/${TD}/check_result" ]; then
                        if "${OFFICE}/${TD}/check_result" "${OFFICE}/results/${TD}_${SOL}_execute/results.yaml"; then
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

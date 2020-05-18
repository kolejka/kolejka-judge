#!/bin/bash
JUDGE_NAME="generic"
LIBRARY="kolejka-judge"
OFFICE="$(readlink -f "$(dirname "$(which "$0")")")"
KOLEJKA="$(dirname "$(readlink -f "$(dirname "$(which "$0")")")")"
JUDGE="${KOLEJKA}/judges/${JUDGE_NAME}"

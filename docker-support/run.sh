#!/bin/bash

SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

echo "Running pre-flight checks..."

SERVICE=$1


if [[ ${SERVICE} == "survey" ]]; then
    echo "Running survey..."
    ${SCRIPT_DIR}/run_survey.sh

elif [[ ${SERVICE} == "worker" ]]; then
    echo "Running worker..."
    ${SCRIPT_DIR}/run_worker.sh

else
    echo "Unknown service ${1}"
fi

#!/bin/bash

# fail on error
set -e
set -o pipefail

if [ -n "$CCW_ARTIFACTS_DIR" ];
then
    DINIT_WORKING_ROOT="${CCW_ARTIFACTS_DIR}/dinit"
else
    if [ -n "$ROS_HOME" ];
    then
        DINIT_WORKING_ROOT="${ROS_HOME}/dinit"
    else
        DINIT_WORKING_ROOT="${HOME}/.ros/dinit"
    fi
fi

VAR_PATTERN='[[:alnum:]_]\+=[[:alnum:]_]*'
read -r -a DINIT_ENVIRONMENT <<< "$(echo "$@" | grep -o "${VAR_PATTERN}" || true)"
read -r -a DINIT_ARGS <<< "$(echo "$@" | sed "s/${VAR_PATTERN}//g")"

env "${DINIT_ENVIRONMENT[@]}" \
    dinitctl \
    --socket-path "${DINIT_WORKING_ROOT}/socket" \
    "${DINIT_ARGS[@]}"

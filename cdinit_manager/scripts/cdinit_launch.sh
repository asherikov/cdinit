#!/bin/bash
# shellcheck disable=SC2001

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

mkdir -p "${DINIT_WORKING_ROOT}"
# how to control a particular instance if there are many?
#DINIT_WORKING_ROOT="${DINIT_WORKING_ROOT}/$(date '+%Y_%m_%d_%H_%M_%S')_XXX"
#DINIT_WORKING_ROOT="$(mktemp -d '${DINIT_WORKING_ROOT}')"

INSTALL_ROOT=$(realpath "$(dirname "$0")/../")
SEARCH_PATHS=( $(echo "${INSTALL_ROOT}:${ROS_PACKAGE_PATH}" | tr ":" " ") )
DINIT_SERVICES_DIR=( $(find "${SEARCH_PATHS[@]}" -type d -name "cdinit_services" | sed "s/^/--services-dir /" | xargs echo) )

VAR_PATTERN='[[:alnum:]_]\+=[[:alnum:]_]*'
DINIT_ENVIRONMENT=( $(echo "$@" | grep -o "${VAR_PATTERN}" || true) )
DINIT_ARGS=( $(echo "$@" | sed "s/${VAR_PATTERN}//g") )
# strip ROS args
DINIT_ARGS=( $(echo "$DINIT_ARGS" | sed "s/__[[:alnum:]_]\+:=[[:graph:]_]*//g") )


env "${DINIT_ENVIRONMENT[@]}" \
    dinit \
    "${DINIT_SERVICES_DIR[@]}" \
    --socket-path "${DINIT_WORKING_ROOT}/socket" \
    --log-file "${DINIT_WORKING_ROOT}/log" \
    --user \
    "${DINIT_ARGS[@]}"

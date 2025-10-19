#!/usr/bin/env bash
#!/bin/bash -x

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

DINIT_SOCKET="${DINIT_WORKING_ROOT}/socket"
DINITCTL=(dinitctl --socket-path "${DINIT_SOCKET}")

INSTALL_ROOT=$(realpath "$(dirname "$0")/../")
IFS=":" read -r -a SEARCH_PATHS <<< "${INSTALL_ROOT}:${ROS_PACKAGE_PATH}"
read -r -a DINIT_SERVICES_DIR <<< "$(find "${SEARCH_PATHS[@]}" -type d -name "cdinit_services" | sed "s/^/--services-dir /" | tr '\n' ' ')"

mkdir -p "${DINIT_WORKING_ROOT}"

if [ ! -S "${DINIT_SOCKET}" ] || (! "${DINITCTL[@]}" status cdinit_main > /dev/null)
then
    dinit \
        "${DINIT_SERVICES_DIR[@]}" \
        --socket-path "${DINIT_SOCKET}" \
        --log-file "${DINIT_WORKING_ROOT}/log" \
        --user \
        cdinit_main &
fi


VAR_PATTERN='[[:alnum:]_]\+=[[:graph:]]*'
readarray -t DINIT_ENVIRONMENT <<< "$(echo "$@" | grep -o "${VAR_PATTERN}" || true)"
read -r -a DINIT_ARGS <<< "$(echo "$@" | sed "s/${VAR_PATTERN}//g")"
# strip ROS args
read -r -a DINIT_ARGS <<< "$(echo "${DINIT_ARGS[@]}" | sed "s/__[[:alnum:]_]\+:=[[:graph:]]*//g")"

if [ ${#DINIT_ENVIRONMENT[@]} -gt 0 ] && [ "${DINIT_ENVIRONMENT[0]}" != "" ]
then
    "${DINITCTL[@]}" setenv "${DINIT_ENVIRONMENT[@]}"
fi

"${DINITCTL[@]}" "${DINIT_SERVICES_DIR[@]}" "${DINIT_ARGS[@]}"

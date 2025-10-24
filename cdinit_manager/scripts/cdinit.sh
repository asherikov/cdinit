#!/usr/bin/env bash
#!/bin/bash -x

# fail on error
set -e
set -o pipefail

###
# Determine working directory
if [ -n "$CCWS_ARTIFACTS_DIR" ];
then
    CDINIT_WORKING_ROOT="${CCWS_ARTIFACTS_DIR}/cdinit"
else
    if [ -n "${ROS_LOG_DIR}" ];
    then
        CDINIT_WORKING_ROOT="${ROS_LOG_DIR}/cdinit"
    else
        CDINIT_WORKING_ROOT="${HOME}/.cache/sharf/cdinit"
    fi
fi
###


CDINIT_SOCKET="${CDINIT_WORKING_ROOT}/socket"
CDINITCTL=(dinitctl --socket-path "${CDINIT_SOCKET}")

# start main if needed
if [ ! -S "${CDINIT_SOCKET}" ] || (! "${CDINITCTL[@]}" status cdinit_main > /dev/null)
then
    echo "cdinit working directory is '${CDINIT_WORKING_ROOT}'"
    mkdir -p "${CDINIT_WORKING_ROOT}"

    ###
    # Generate session id
    CDINIT_SESSION_ID=$(mktemp --directory --dry-run "session_$(date +%Y%m%d_%H%M%S)_$(printf "%05d" "$(find "${CDINIT_WORKING_ROOT}" -maxdepth 1 -name "session_*" | wc -l)")_XXXXX")
    CDINIT_SESSION_ROOT=${CDINIT_WORKING_ROOT}/${CDINIT_SESSION_ID}
    echo "cdinit session root is '${CDINIT_SESSION_ROOT}'"
    mkdir -p "${CDINIT_SESSION_ROOT}"
    ###

    ###
    # Find service directories
    CDINIT_INSTALL_ROOT=$(realpath "$(dirname "$0")/../")
    IFS=":" read -r -a SEARCH_PATHS <<< "$(echo "${CDINIT_INSTALL_ROOT}:${ROS_PACKAGE_PATH}:${AMENT_PREFIX_PATH}" | sed -e "s/:\+/:/g" -e "s/^://" -e "s/:$//")"
    read -r -a CDINIT_SERVICES_DIR <<< "$(find "${SEARCH_PATHS[@]}" -type d -name "cdinit_services" | sed "s/^/--services-dir /" | tr '\n' ' ')"
    ###

    dinit \
        "${CDINIT_SERVICES_DIR[@]}" \
        --socket-path "${CDINIT_SOCKET}" \
        --log-file "${CDINIT_WORKING_ROOT}/log" \
        --user \
        cdinit_main &
    while [ ! -S "${CDINIT_SOCKET}" ]
    do
        sleep 0.05
    done

    "${CDINITCTL[@]}" setenv "CDINIT_INSTALL_ROOT=${CDINIT_INSTALL_ROOT}"
    "${CDINITCTL[@]}" setenv "CDINIT_WORKING_ROOT=${CDINIT_WORKING_ROOT}"
    "${CDINITCTL[@]}" setenv "CDINIT_SESSION_ROOT=${CDINIT_SESSION_ROOT}"
    "${CDINITCTL[@]}" setenv "CDINIT_SESSION_ID=${CDINIT_SESSION_ID}"
fi

###
# Set user provided variables
VAR_PATTERN='[[:alnum:]_]\+=[[:graph:]]*'
readarray -t CDINIT_ENVIRONMENT <<< "$(echo "$@" | grep -o "${VAR_PATTERN}" || true)"

if [ ${#CDINIT_ENVIRONMENT[@]} -gt 0 ] && [ "${CDINIT_ENVIRONMENT[0]}" != "" ]
then
    "${CDINITCTL[@]}" setenv "${CDINIT_ENVIRONMENT[@]}"
fi
###

# strip user provided variables
read -r -a CDINIT_ARGS <<< "$(echo "$@" | sed "s/${VAR_PATTERN}//g")"
# strip ROS args
read -r -a CDINIT_ARGS <<< "$(echo "${CDINIT_ARGS[@]}" | sed "s/__[[:alnum:]_]\+:=[[:graph:]]*//g")"
if [ "${#CDINIT_ARGS[@]}" -gt 0 ] && [ "${CDINIT_ARGS[0]}" != "" ]
then
    "${CDINITCTL[@]}" "${CDINIT_SERVICES_DIR[@]}" "${CDINIT_ARGS[@]}"
fi

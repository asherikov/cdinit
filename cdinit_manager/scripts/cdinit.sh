#!/usr/bin/env bash
#!/bin/bash -x

# fail on error
set -e
set -o pipefail

if [ -n "$CCW_ARTIFACTS_DIR" ];
then
    CDINIT_WORKING_ROOT="${CCW_ARTIFACTS_DIR}/cdinit"
else
    if [ -n "${ROS_LOG_DIR}" ];
    then
        CDINIT_WORKING_ROOT="${ROS_LOG_DIR}/cdinit"
    else
        CDINIT_WORKING_ROOT="${HOME}/.sharf/cdinit"
    fi
fi

CDINIT_SOCKET="${CDINIT_WORKING_ROOT}/socket"
CDINITCTL=(dinitctl --socket-path "${CDINIT_SOCKET}")

INSTALL_ROOT=$(realpath "$(dirname "$0")/../")
IFS=":" read -r -a SEARCH_PATHS <<< "${INSTALL_ROOT}:${ROS_PACKAGE_PATH}"
read -r -a CDINIT_SERVICES_DIR <<< "$(find "${SEARCH_PATHS[@]}" -type d -name "cdinit_services" | sed "s/^/--services-dir /" | tr '\n' ' ')"

mkdir -p "${CDINIT_WORKING_ROOT}"
echo "cdinit working directory is '${CDINIT_WORKING_ROOT}'"

if [ ! -S "${CDINIT_SOCKET}" ] || (! "${CDINITCTL[@]}" status cdinit_main > /dev/null)
then
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
    "${CDINITCTL[@]}" setenv "CDINIT_WORKING_ROOT=${CDINIT_WORKING_ROOT}"
fi


VAR_PATTERN='[[:alnum:]_]\+=[[:graph:]]*'
readarray -t CDINIT_ENVIRONMENT <<< "$(echo "$@" | grep -o "${VAR_PATTERN}" || true)"
read -r -a CDINIT_ARGS <<< "$(echo "$@" | sed "s/${VAR_PATTERN}//g")"
# strip ROS args
read -r -a CDINIT_ARGS <<< "$(echo "${CDINIT_ARGS[@]}" | sed "s/__[[:alnum:]_]\+:=[[:graph:]]*//g")"

if [ ${#CDINIT_ENVIRONMENT[@]} -gt 0 ] && [ "${CDINIT_ENVIRONMENT[0]}" != "" ]
then
    "${CDINITCTL[@]}" setenv "${CDINIT_ENVIRONMENT[@]}"
fi

"${CDINITCTL[@]}" "${CDINIT_SERVICES_DIR[@]}" "${CDINIT_ARGS[@]}"

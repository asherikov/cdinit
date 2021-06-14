#!/bin/sh


DINIT_INSTALL_ROOT=$(rospack find cdinit)


if [ -n "$CCW_ARTIFACTS_DIR" ]; 
then
    DINIT_WORKING_ROOT=${CCW_ARTIFACTS_DIR}/dinit/
else
    DINIT_WORKING_ROOT=${ROS_HOME}/dinit/
fi
mkdir -p "${DINIT_WORKING_ROOT}"


DINIT_SERVICES_DIR=$(find $(echo "${ROS_PACKAGE_PATH}" | tr ":" " ") -type d -name "dinit_services" | sed "s/^/--services-dir /" | xargs echo)


rosrun cdinit dinit \
    ${DINIT_SERVICES_DIR} \
    --socket-path "${DINIT_WORKING_ROOT}/socket" \
    --log-file "${DINIT_WORKING_ROOT}/log" \
    --user \
    $@

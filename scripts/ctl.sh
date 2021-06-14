#!/bin/sh

if [ -n "$CCW_ARTIFACTS_DIR" ]; 
then
    DINIT_WORKING_ROOT=${CCW_ARTIFACTS_DIR}/dinit/
else
    DINIT_WORKING_ROOT=${ROS_HOME}/dinit/
fi

rosrun cdinit dinitctl \
    --socket-path "${DINIT_WORKING_ROOT}/socket" \
    $@

#!/bin/sh

DINIT_WORKING_ROOT=${CCW_ARTIFACTS_DIR}/dinit/

rosrun cdinit dinitctl \
    --socket-path "${DINIT_WORKING_ROOT}/socket" \
    $@

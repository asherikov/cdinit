#!/bin/sh

DINIT_INSTALL_ROOT=$(rospack find cdinit)
DINIT_WORKING_ROOT=${CCW_ARTIFACTS_DIR}/dinit/

mkdir -p "${DINIT_WORKING_ROOT}"

rosrun cdinit dinit \
    --services-dir "${DINIT_INSTALL_ROOT}/examples" \
    --socket-path "${DINIT_WORKING_ROOT}/socket" \
    --log-file "${DINIT_WORKING_ROOT}/log" \
    --user \
    roscore

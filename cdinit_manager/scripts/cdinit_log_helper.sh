#!/usr/bin/env bash

# fail on error
set -e
set -o pipefail

ts '%.s' | cat >> "${CDINIT_SESSION_ROOT}/$1.log"


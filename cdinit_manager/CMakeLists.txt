cmake_minimum_required(VERSION 3.8.0)
project(cdinit_manager NONE)

#############
## Install ##
#############

install(PROGRAMS
    scripts/cdinit_ctl.sh
    scripts/cdinit_launch.sh
    DESTINATION bin
)

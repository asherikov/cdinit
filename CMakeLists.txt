cmake_minimum_required(VERSION 3.8.0)
project(cdinit CXX)


#########################
# configuration

set(DINIT_CONFIG_DIR "${CMAKE_BINARY_DIR}/buildconfig/includes/")
file(MAKE_DIRECTORY "${DINIT_CONFIG_DIR}")

set(DINIT_CONFIG_HEADER "${DINIT_CONFIG_DIR}/mconfig.h")
set(DINIT_SBINDIR "/sbin")
set(DINIT_SYSCONTROLSOCKET "") # should be specified in command line
set(DINIT_VERSION "0.19.4")

add_executable(mconfig-gen
    dinit/build/tools/mconfig-gen.cc
)

add_custom_command(
    COMMAND mconfig-gen DEFAULT_AUTO_RESTART=NEVER SBINDIR=${DINIT_SBINDIR} SYSCONTROLSOCKET=${DINIT_SYSCONTROLSOCKET} VERSION=${DINIT_VERSION} > ${DINIT_CONFIG_HEADER}
    DEPENDS mconfig-gen
    OUTPUT ${DINIT_CONFIG_HEADER}
)
#########################


#########################
# executables
include_directories(
    dinit/src/includes
    dinit/dasynq/include/
    ${DINIT_CONFIG_DIR}
)


add_executable(dinitctl
    dinit/src/dinitctl.cc
    dinit/src/options-processing.cc
    dinit/src/settings.cc
    ${DINIT_CONFIG_HEADER}
)

add_executable(dinitcheck
    dinit/src/dinitcheck.cc
    dinit/src/options-processing.cc
    dinit/src/settings.cc
    ${DINIT_CONFIG_HEADER}
)

add_executable(dinitmonitor
    dinit/src/dinit-monitor.cc
    ${DINIT_CONFIG_HEADER}
)

add_executable(dinit
    dinit/src/dinit.cc
    dinit/src/load-service.cc
    dinit/src/service.cc
    dinit/src/proc-service.cc
    dinit/src/baseproc-service.cc
    dinit/src/control.cc
    dinit/src/dinit-log.cc
    dinit/src/dinit-main.cc
    dinit/src/run-child-proc.cc
    dinit/src/options-processing.cc
    dinit/src/dinit-env.cc
    dinit/src/settings.cc
    ${DINIT_CONFIG_HEADER}
)
#########################



#############
## Install ##
#############

install(TARGETS dinit dinitctl dinitcheck
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

foreach(DIR dinit_services scripts)
    install(DIRECTORY ${DIR}
        DESTINATION share/${PROJECT_NAME}/
        USE_SOURCE_PERMISSIONS
    )
endforeach()

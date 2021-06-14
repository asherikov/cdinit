cmake_minimum_required(VERSION 3.0.0)
project(cdinit)

find_package(catkin REQUIRED)


###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if your package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
#    INCLUDE_DIRS include
#    LIBRARIES ${PROJECT_NAME}
#    CATKIN_DEPENDS ...
#    DEPENDS system_lib
)


###########
## Build ##
###########

# --------------
# CCW flags
# --------------
#if (CCW_CLANG_TIDY)
#    set (CMAKE_CXX_CLANG_TIDY "${CCW_CLANG_TIDY}")
#endif()
#if (CCW_CXX_FLAGS)
#    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CCW_CXX_FLAGS} -Wno-unused-parameter -Wno-shadow -Wno-overflow")
#    set (CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${CCW_LINKER_FLAGS}")
#endif()
# --------------



#########################
# configuration

set(DINIT_CONFIG_DIR "${CMAKE_BINARY_DIR}/buildconfig/includes/")
file(MAKE_DIRECTORY "${DINIT_CONFIG_DIR}")

set(DINIT_CONFIG_HEADER "${DINIT_CONFIG_DIR}/mconfig.h")
set(DINIT_SBINDIR "/sbin")
set(DINIT_SYSCONTROLSOCKET "") # should be specified in command line
set(DINIT_VERSION "0.11.0")

add_executable(mconfig-gen
    dinit/build/tools/mconfig-gen.cc
)

add_custom_command(
    COMMAND mconfig-gen SBINDIR=${DINIT_SBINDIR} SYSCONTROLSOCKET=${DINIT_SYSCONTROLSOCKET} VERSION=${DINIT_VERSION} > ${DINIT_CONFIG_HEADER}
    DEPENDS mconfig-gen
    OUTPUT ${DINIT_CONFIG_HEADER}
)
#########################



#########################
# executables

include_directories(
    dinit/src/includes
    dinit/src/dasynq
    ${DINIT_CONFIG_DIR}
)


add_executable(dinitctl
    dinit/src/dinitctl.cc
    ${DINIT_CONFIG_HEADER}
)

add_executable(dinitcheck
    dinit/src/dinitcheck.cc
    dinit/src/options-processing.cc
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
    ${DINIT_CONFIG_HEADER}
)
#########################


## Rename C++ executable without prefix
## The above recommended prefix causes long target names, the following renames the
## target back to the shorter version for ease of user use
## e.g. "rosrun someones_pkg node" instead of "rosrun someones_pkg someones_pkg_node"
#set_target_properties(${PROJECT_NAME}_node PROPERTIES OUTPUT_NAME node PREFIX "")



#############
## Install ##
#############

# Mark executables and/or libraries for installation
install(TARGETS dinit dinitctl dinitcheck
    ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
    LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
    RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

foreach(DIR dinit_services scripts)
    install(DIRECTORY ${DIR}
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
        USE_SOURCE_PERMISSIONS
    )
endforeach()

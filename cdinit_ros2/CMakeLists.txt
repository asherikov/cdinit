cmake_minimum_required(VERSION 3.8.0)
project(cdinit_ros2 NONE)

#############
## Install ##
#############

foreach(DIR cdinit_services config)
    install(DIRECTORY ${DIR}
        DESTINATION share/${PROJECT_NAME}/
        USE_SOURCE_PERMISSIONS
    )
endforeach()

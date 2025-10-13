cmake_minimum_required(VERSION 3.8.0)
project(cdinit_examples NONE)

#############
## Install ##
#############

foreach(DIR cdinit_services)
    install(DIRECTORY ${DIR}
        DESTINATION share/${PROJECT_NAME}/
        USE_SOURCE_PERMISSIONS
    )
endforeach()

#
# AppUpdate
#
cmake_minimum_required(VERSION 3.14)

set(APPNAME AppUpdate)
project(${APPNAME})

set(HEADER_FILES)


set(SOURCE_FILES
    src/app_update.cpp
)


add_executable(${APPNAME}
  ${SOURCE_FILES}
  ${HEADER_FILES}
  ${RESOURCE_FILES}
  ${VERSION_SOURCE_FILES}
  ${QT_GUI_FORMS_HEADERS}
  ${RESOURCE_ADDED}
)
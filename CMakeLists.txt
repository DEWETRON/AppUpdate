#
# AppUpdate
#
cmake_minimum_required(VERSION 3.14)

set(APPNAME AppUpdate)
project(${APPNAME})

#
# define SW_APP_ROOT == Projects root directory
get_filename_component(SW_APP_ROOT . ABSOLUTE)


# expand cmake search path to check for project settings
set(CMAKE_MODULE_PATH
  ${CMAKE_MODULE_PATH}
  ${SW_APP_ROOT}/cmake
)

include(QtSettings)

message(STATUS "=Build Settings======================================================")
message(STATUS "QT_VERSION      = ${QT_VERSION}")
message(STATUS "=====================================================================")

set(CMAKE_AUTOMOC ON)
find_package(Qt5Core)
find_package(Qt5Widgets)
find_package(Qt5Network)

include_directories(
  inc
  ${CMAKE_CURRENT_BINARY_DIR}
)

set(HEADER_FILES
  inc/au_window.h
)


set(SOURCE_FILES
  src/app_update.cpp
  src/au_window.cpp
)


add_executable(${APPNAME}
  ${SOURCE_FILES}
  ${HEADER_FILES}
  ${RESOURCE_FILES}
  ${VERSION_SOURCE_FILES}
  ${QT_GUI_FORMS_HEADERS}
  ${RESOURCE_ADDED}
)

if (WIN32)
  target_link_libraries(${APPNAME}
    Qt5::WinMain
    ws2_32.lib
  )
endif()

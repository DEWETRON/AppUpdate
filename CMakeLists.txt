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

# Instruct CMake to run moc automatically when needed.
set(CMAKE_AUTOMOC ON)
# Whether to handle rcc automatically for Qt targets.
set(CMAKE_AUTORCC ON)

find_package(Qt5Core)
find_package(Qt5Widgets)
find_package(Qt5Network)

include_directories(
  inc
  ${CMAKE_CURRENT_BINARY_DIR}
)

set(AU_HEADER_FILES
  inc/au_window.h
)

set(AU_SOURCE_FILES
  src/app_update.cpp
  src/au_window.cpp
)

set(AU_RESOURCE_FILES
  res/au_resources.qrc
)
qt5_add_resources(RESOURCE_ADDED ${QT_RESOURCE_FILES})

add_executable(${APPNAME} WIN32
  ${AU_SOURCE_FILES}
  ${AU_HEADER_FILES}
  ${AU_RESOURCE_FILES}
  ${VERSION_SOURCE_FILES}
  ${QT_GUI_FORMS_HEADERS}
  ${RESOURCE_ADDED}
)

qt5_use_modules(${APPNAME} Widgets)

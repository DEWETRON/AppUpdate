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

find_package(Qt5Core REQUIRED)
find_package(Qt5Quick)
find_package(Qt5Network)
find_package(Qt5Widgets)

include_directories(
  inc
  ${CMAKE_CURRENT_BINARY_DIR}
)


add_subdirectory(qml)

set(AU_HEADER_FILES
  inc/au_application.h
  inc/au_application_data.h
  inc/au_downloader.h
  inc/au_window_qml.h
  inc/au_software_enumerator.h
  inc/au_update_json.h
)

set(AU_SOURCE_FILES
  src/app_update.cpp
  src/au_application.cpp
  src/au_application_data.cpp
  src/au_downloader.cpp
  src/au_window_qml.cpp
  src/au_software_enumerator.cpp
  src/au_update_json.cpp
)

if(WIN32)
  set(AU_HEADER_FILES
    ${AU_HEADER_FILES}
    inc/au_registry_win.h
  )
  set(AU_SOURCE_FILES
    ${AU_SOURCE_FILES}
    src/au_registry_win.cpp
  )
endif()

if(UNIX)
  set(AU_HEADER_FILES
    ${AU_HEADER_FILES}
    inc/au_dpkg_lin.h
  )
  set(AU_SOURCE_FILES
    ${AU_SOURCE_FILES}
    src/au_dpkg_lin.cpp
  )
endif()


set(QT_HEADER_FILES
  inc/qml_reloader.h
)

set(QT_SOURCE_FILES
  src/qml_reloader.cpp
)


set(AU_RESOURCE_FILES
  res/au_resources.qrc
)
qt5_add_resources(RESOURCE_ADDED ${QT_RESOURCE_FILES})

add_executable(${APPNAME} WIN32
  ${AU_SOURCE_FILES}
  ${AU_HEADER_FILES}
  ${AU_RESOURCE_FILES}
  ${QT_HEADER_FILES}
  ${QT_SOURCE_FILES}
  ${VERSION_SOURCE_FILES}
  ${QT_GUI_FORMS_HEADERS}
  ${RESOURCE_ADDED}
)

qt5_use_modules(${APPNAME} Widgets Quick)

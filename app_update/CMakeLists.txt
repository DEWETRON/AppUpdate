#
# AppUpdate
#
cmake_minimum_required(VERSION 3.14)

set(APPNAME AppUpdate)
project(${APPNAME})

#
# define SW_APP_ROOT == Projects root directory
get_filename_component(SW_APP_ROOT .. ABSOLUTE)


# expand cmake search path to check for project settings
set(CMAKE_MODULE_PATH
  ${CMAKE_MODULE_PATH}
  ${SW_APP_ROOT}/build_util/cmake
)

include(QtSettings)
include(CMakeInstallUtil)

#
# Check for 64 bit build
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(BUILD_X64 TRUE)
  set(BUILD_X86 FALSE)
  set(architecture "x64")
else()
  set(BUILD_X64 FALSE)
  set(BUILD_X86 TRUE)
  set(architecture "x86")
endif()

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
  au_resources.qrc
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


#
# Install section
#

#
# Install should not depend on ALL
set(CMAKE_SKIP_INSTALL_ALL_DEPENDENCY TRUE)

if (WIN32)
  # install binary
  set(RUNTIME_PATH ${CMAKE_INSTALL_PREFIX}/${architecture})
  install(FILES "res/qt.conf" DESTINATION ${RUNTIME_PATH})

  install(TARGETS ${APPNAME}
          RUNTIME DESTINATION ${RUNTIME_PATH})

  # install QT libs (dll's) ..
  set(PACKAGE "widgets quick2 network" )
  InstallQTRuntimeSinglePackage(${SW_APP_ROOT} ${CMAKE_INSTALL_PREFIX}/${architecture} widgets ${QT_VERSION})
  InstallQTRuntimeSinglePackage(${SW_APP_ROOT} ${CMAKE_INSTALL_PREFIX}/${architecture} quick2 ${QT_VERSION})
  InstallQTRuntimeSinglePackage(${SW_APP_ROOT} ${CMAKE_INSTALL_PREFIX}/${architecture} network ${QT_VERSION})

  # example update json
  install(FILES examples/update.json DESTINATION ${RUNTIME_PATH}/examples)
  install(FILES res/dewetron.ico DESTINATION ${RUNTIME_PATH}/res)

  # QT: qml and more
  if (NOT PACK_QML_FILES)
    install(DIRECTORY qml DESTINATION ${CMAKE_INSTALL_PREFIX}/${architecture})
  endif()

endif()

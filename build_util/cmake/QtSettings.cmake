#
# Qt build settings for Windows, Linux, macOS
#

#
# QtSettings is a cmake helper module to detect and configure Qt.
#
# It can be configured with following variables:
#
# * QT_VERSION use a specific version Qt (default = 5.12.6)
# * QT_BASE_PATH point to a Qt installation (default = "")
# * QT_CANDIDATES is a list of supported Qt versions
# * QT_DIRS list of commonly used Qt install directories

if(my_module_QtSettings_included)
  return()
endif(my_module_QtSettings_included)
set(my_module_QtSettings_included true)


if (NOT SW_APP_ROOT)
  get_filename_component(SW_APP_ROOT .. ABSOLUTE)
endif()

# default qt list
set(QT_CANDIDATES "5.12.6;5.12.5")


if (QT_BASE_PATH)
  get_filename_component(_qt_base_path ${CMAKE_CURRENT_SOURCE_DIR}/${QT_BASE_PATH} ABSOLUTE)
endif()

set(QT_DIRS
  "${_qt_base_path}"
  "${SW_APP_ROOT}/3rdparty/qt"
  "/opt/qt"
  "C:/Qt"
)


message(STATUS "=Qt Settings=========================================================")


# find correct qt variant for current build
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(QT_BUILD_BITS 64)
else()
  set(QT_BUILD_BITS 32)
endif()

if(WIN32)
  set(QT_BUILD_SYSTEM "win")
elseif(APPLE)
  set(QT_BUILD_SYSTEM "osx")
elseif(UNIX)
  set(QT_BUILD_SYSTEM "lin")
else()
  set(QT_BUILD_SYSTEM "unknown")
endif()


# Detect qt and set QT_VERSION if unset
if(NOT QT_VERSION)
  
  # set default
  set(QT_VERSION "5.12.6")

  if (WIN32)

    set(_detected false)

    foreach(_qt ${QT_CANDIDATES})

      foreach(_qt_dir ${QT_DIRS})
      # path without separate version dir
      set(_this_qt "${_qt_dir}")
      message(STATUS "looking for ${_this_qt}")
      if (EXISTS ${_this_qt})
        get_filename_component(qt_base_name ${_this_qt} NAME)
        string(LENGTH ${_qt} qt_ver_len)
        string(SUBSTRING  ${qt_base_name} 0 ${qt_ver_len} qt_prefix)
        if ("${qt_prefix}" EQUAL "${_qt}")
          set(QT_VERSION ${_qt})
          message(STATUS "detected ${QT_VERSION} (1)")
          set(_detected true)
          get_filename_component(_qt_base_path ${_this_qt} ABSOLUTE)
          break()
        endif()
      endif()

      if (${_detected})
        break()
      endif()

      # path with separate version dir
      set(_this_qt "${_qt_dir}/${_qt}")
        message(STATUS "looking for ${_this_qt}")
        if (EXISTS ${_this_qt})
          set(QT_VERSION ${_qt})
          message(STATUS "detected ${QT_VERSION} (2)")
          set(_detected true)
          get_filename_component(_qt_base_path ${_this_qt} ABSOLUTE)
          break()
        endif()
        endforeach()

      if (${_detected})
        break()
      endif()

    endforeach()
    message(STATUS "Qt version detected (${QT_VERSION})")
  endif()
endif()

# find Qt cmake support files
find_path(QT_CMAKE_PATH Qt5/Qt5Config.cmake
  ${_qt_base_path}/lib/cmake
)

# extend CMAKE_PREFIX_PATH
set(CMAKE_PREFIX_PATH
  ${CMAKE_PREFIX_PATH}
  ${QT_CMAKE_PATH}
)

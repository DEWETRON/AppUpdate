#
# Use deploy_qt.py to copy a single lib & its dependencies
# param SW_APP_ROOT
# param DEST_DIR
# param packages ..
macro(InstallQTRuntimeSinglePackage SW_APP_ROOT DEST_DIR PACKAGE QT_VERSION)

  set(_qt_version "5.9.2")

  if (QT_VERSION)
    set(_qt_version ${QT_VERSION})
  endif()

  if (QT_SPECIAL_VERSION)
    set(_qt_special_build "--special-build ${QT_SPECIAL_VERSION}")
  endif()

  get_filename_component(_abs_qt_full_path ${QT_BASE_PATH} ABSOLUTE)
  get_filename_component(_abs_qt_path ${_abs_qt_full_path} DIRECTORY)


  if (BUILD_X64)
    install(CODE "
  # InstallQTRuntimeLibraries begin
  #
  # just defer the task to the deploy script
  execute_process(
    COMMAND python \"${SW_APP_ROOT}/build_util/bin/deploy_qt.py\" --arch x64 --build_type Release --qt-directory ${_abs_qt_path} --qt-module ${PACKAGE} --dest ${DEST_DIR} --qt-version ${_qt_version} ${_qt_special_build}
    )

  # InstallQTRuntimeLibraries end
   "
    COMPONENT RUNTIME)
  elseif(BUILD_X86)
    install(CODE "
  # InstallQTRuntimeLibraries begin
  #
  # just defer the task to the deploy script
  execute_process(
    COMMAND python \"${SW_APP_ROOT}/build_util/bin/deploy_qt.py\" --arch x86 --build_type Release --qt-directory ${_abs_qt_path} --qt-module ${PACKAGE} --dest ${DEST_DIR} --qt-version ${_qt_version} ${_qt_special_build}
    )

  # InstallQTRuntimeLibraries end
   "
    COMPONENT RUNTIME)
  endif()

endmacro()

macro(get_arch ARCH)
  set(_ARCH "x64")  #default
  if (BUILD_X86)
    set(_ARCH "x86")
  endif()
  if (BUILD_X64)
    set(_ARCH "x64")
  endif()
endmacro()

#
# Install openssl
macro(install_openssl SW_APP_ROOT DEST_DIR OPEN_SSL_PATH)
  get_arch(_ARCH)
  if (BUILD_X64)
    install(FILES ${OPEN_SSL_PATH}/libcrypto-1_1-x64.dll DESTINATION ${DEST_DIR})
    install(FILES ${OPEN_SSL_PATH}/libssl-1_1-x64.dll DESTINATION ${DEST_DIR})
  else()
    install(FILES ${OPEN_SSL_PATH}/libcrypto-1_1.dll DESTINATION ${DEST_DIR})
    install(FILES ${OPEN_SSL_PATH}/libssl-1_1.dll DESTINATION ${DEST_DIR})
  endif()
endmacro()

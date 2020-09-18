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

#!/usr/bin/env python
import argparse
import os
import subprocess
import sys

ARCH_X86      = 'x86'
ARCH_X64      = 'x64'

def deploy_qt(script_path, destination, qt_directory, arch, build_type, special_build, version, install_qt_ut_libs):
    deploy_script_path = os.path.join(script_path, "deploy_qt.py")
    args = "--destination \"%s\" --qt-directory \"%s\" --arch %s --build-type %s --qt-version %s --qt-module widgets --qt-module quick2 --qt-module network" % (destination, qt_directory, arch, build_type, version)
    if (special_build):
        args = args + " --special-build %s" % (special_build)
    if (install_qt_ut_libs):
        args = args + " --qt_module test"
    command = deploy_script_path + " " + args
    print(command)
    os.system(command)

def main(argv):
    script_path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    #repo_root = os.path.normpath(os.path.join(script_path, ".."+os.sep+".."))
    repo_root = script_path
    build_util_bin_path = os.path.normpath(os.path.join(repo_root, "script"))

    print(build_util_bin_path)
    sys.path.append(build_util_bin_path)

    parser = argparse.ArgumentParser(description='deploy_3rdparty_libs.py copies all necessary runtime files for dewetron explorer')
    parser.add_argument('--arch', dest='architecture',
                        action='store',
                        choices=[ARCH_X86,ARCH_X64],
                        default=ARCH_X64,
                        help='select the architecture of the build (x86 = 32bit, x64 = 64bit)')

    parser.add_argument('--build-type', '--build_type', dest='build_type',
                        action='store',
                        choices=['Debug','Release'],
                        default='Release',
                        help='set the optimization of the build. Release is the default')

    parser.add_argument('--destination', dest='destination',
                        action='store',
                        default=None,
                        help='specify the directory where qt will be deployed')

    parser.add_argument('--qt-directory', dest='qt_directory',
                        action='store',
                        default=None,
                        help='specify the directory where the qt install directories are located')

    parser.add_argument('--qt-version', '--qt_version', dest='qt_version',
                        action='store',
                        choices=['5.12.6', '5.12.5'],
                        default='5.12.6',
                        help='specify the qt version to be deployed')

    parser.add_argument('--qt-test', '--qt_test', dest='qt_debug',
                        action='store',
                        choices=['false', 'true'],
                        default='false',
                        help='set true if qt debug libs should be deployed')

    parser.add_argument('--qt-special-build', '--qt_special_build', dest='qt_special_build',
                        action='store',
                        default='angle',
                        help='select a special build variant (e.g. "angle")')

    args = parser.parse_args()

    print(args)

    if not args.destination:
        print("Error: please specify --destination folder")
        return 1

    destination_path = os.path.abspath(args.destination)

    deploy_qt(build_util_bin_path, destination_path, args.qt_directory, args.architecture, args.build_type, args.qt_special_build, args.qt_version, args.qt_debug == 'true')
    return 0

#----------------------------------------------------------------------
# main
if __name__ == "__main__":
    ret = main(sys.argv)
    sys.exit(ret)

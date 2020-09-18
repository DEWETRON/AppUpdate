#!/usr/bin/env python
"""
This script is used to generate a workspaces using CMake
Copyright (c) Dewetron 2012
"""

# pylint: disable=import-error

from __future__ import print_function
import argparse
import os
import subprocess
import sys
import re

ARCH_X86 = 'x86'
ARCH_X64 = 'x64'
ARCH_X38 = 'x38'
ARCH_PI = 'pi'

DEFAULT_ARCH = [ARCH_X64]

DEFAULT_BUILD = ['Debug']

BUILD_DIR_X86 = 'build'
BUILD_DIR_X64 = 'build64'
BUILD_DIR_X38 = 'buildx38'
BUILD_DIR_PI = 'buildpi'

BUILD_DIR_MANUAL = None

DEFAULT_STUDIO_VERSION = '16'


#----------------------------------------------------------------------
def print_verbose(text):
    """
    print_verbose
    """
    if opt_verbose:
        print(text)
        sys.stdout.flush()

def print_flush(text):
    """
    print_flush
    """
    print(text)
    sys.stdout.flush()

#----------------------------------------------------------------------
def check_cmake_pre_python33():
    """
    check_cmake_pre_python33
    """
    try:
        subprocess.check_call(['cmake', '--version'])
    except OSError as error:
        raise RuntimeError('cmake not found? (%s)' % str(error))
    except subprocess.CalledProcessError as error:
        raise RuntimeError('cmake problem (CalledProcessError) (%s)' % str(error))
    except error:
        raise RuntimeError('cmake problem (unknown error) (%s)' % str(error))
    return None

def check_cmake():
    """
    check_cmake
    """
    if sys.version_info < (3, 3):
        return check_cmake_pre_python33()

    version_info = ''
    try:
        version_info = subprocess.check_output(['cmake', '--version'])
    except OSError as error:
        raise RuntimeError('cmake not found? (%s)' % str(error))
    except subprocess.CalledProcessError as error:
        raise RuntimeError('cmake problem (CalledProcessError) (%s)' % str(error))
    except error:
        raise RuntimeError('cmake problem (unknown error) (%s)' % str(error))

    match = re.search(r'ersion\s+(?P<Major>[0-9]+)\.(?P<Minor>[0-9]+)', str(version_info))
    if match:
        return (int(match.group('Major')), int(match.group('Minor')))
    return None


class CMakeVsGenerator:
    """
    Utility class for generating the correct Generator name for cmake (visual studio)
    +toolset
    """

    def __init__(self, arch, prj_build_config):
        """
        """
        self.__arch = arch
        self.__vs_version = prj_build_config.get('vs_version', None)
        self.__prj_build_config = prj_build_config
        

    def get_visual_studio_generator_name(self):
        """
        get_visual_studio_generator_name
        """
        visual_studio_names = {
            '9'  : 'Visual Studio 9 2008 [arch]',
            '10' : 'Visual Studio 10 2010 [arch]',
            '11' : 'Visual Studio 11 2012 [arch]',
            '12' : 'Visual Studio 12 2013 [arch]',
            '14' : 'Visual Studio 14 2015 [arch]',
            '15' : 'Visual Studio 15 2017 [arch]',
            '16' : 'Visual Studio 16 2019'
        }

        vs_gen_name = visual_studio_names.get(self.__vs_version, None)
        vs_architectures = {
            ARCH_X86 : '',
            ARCH_X64 : 'Win64'
        }
        vs_arch = vs_architectures.get(self.__arch, None)
        
        vs_generator = vs_gen_name.replace('[arch]', vs_arch)

        return vs_generator.strip()

    def get_toolset(self):
        """
        get_toolset(self):
        """
        toolset = []
        toolset_arg = ''

        # Visual Studio 2017 or better support toolsets
        if int(self.__vs_version) < 15:
            return []

        cmake_version = check_cmake()

        # toolset must be first (v140, v141, v142 ...)
        cmake_toolset = self.__prj_build_config.get('cmake_toolset', [])
        if cmake_toolset:
            toolset = cmake_toolset
        
        if cmake_version and cmake_version >= (3, 8):
            if self.__arch == ARCH_X64:
                toolset = toolset + ['host=x64']
            elif self.__arch == ARCH_X86:
                toolset = toolset + ['host=x64']    # always use 64bit toolchain (out of memory linker error)

        if toolset:
            toolset_arg = '-T'
            for t in toolset:
                toolset_arg = toolset_arg + t + ','
            toolset_arg = toolset_arg[:-1]

        return toolset_arg


    def get_arch(self):
        """
        """
        # Visual Studio 2019 or better support -A
        if int(self.__vs_version) >= 16:
            if self.__arch == ARCH_X64:
                return [ '-A', ARCH_X64 ]
            if self.__arch == ARCH_X86:
                return [ '-A', 'Win32' ]
        return []

    def get_cmake_args(self):
        """
        get_cmake_args(self)
        """
        cmake_args = [ '-G', self.get_visual_studio_generator_name()]

        if self.get_toolset():            
            cmake_args = cmake_args + [ self.get_toolset() ]

        if self.get_arch():            
            cmake_args = cmake_args + self.get_arch()

        return cmake_args


class BuildDir(object):
    """
    Capsulate function for managing the (temporary) build directory.
    """
    def __init__(self, arch, builddir):
        """
        ctor
        """
        self.__arch = arch
        self.__builddir = builddir

    def get_build_dir(self):
        """
        get_build_dir
        """
        # manually overriden
        if self.__builddir != None:
            # set the global for function "is_valid_build_dir"
            global BUILD_DIR_MANUAL
            BUILD_DIR_MANUAL = self.__builddir
            return self.__builddir

        # default use arch
        if self.__arch == ARCH_X86:
            return BUILD_DIR_X86
        elif self.__arch == ARCH_X64:
            return BUILD_DIR_X64
        elif self.__arch == ARCH_X38:
            return BUILD_DIR_X38
        elif self.__arch == ARCH_PI:
            return BUILD_DIR_PI

        # default is build
        return "build"


    def create_build_dir(self):
        """
        Create a build directory according to the given architecture
        """
        print_verbose("create_build_dir")
        if opt_dryrun:
            print_flush("dryrun: create_build_dir")
            return
        try:
            os.mkdir(self.get_build_dir())
        except OSError:
            # dir exists. this is no problem
            pass

    #----------------------------------------------------------------------
    def change_to_build_dir(self):
        """
        Change to build dir
        """
        print_verbose("change_to_build_dir")
        if opt_dryrun:
            print_flush("dryrun: change_to_build_dir")
            return

        if os.path.exists(self.get_build_dir()):
            os.chdir(self.get_build_dir())
        else:
            raise RuntimeError("Error: %s not existing" % self.get_build_dir())

#----------------------------------------------------------------------
def is_valid_build_dir():
    """
    is_valid_build_dir
    """
    build_sub_dir = os.path.basename(os.getcwd())

    if 'build' in build_sub_dir:
        return True
    if BUILD_DIR_MANUAL != None:
        return True
    return False

#----------------------------------------------------------------------
def clean_cmake_cache():
    """
    clean_cmake_cache
    """
    print_verbose("clean_cmake_cache")
    if opt_dryrun:
        print_flush("dryrun: clean_cmake_cache")
        return
    if is_valid_build_dir():
        try:
            # remove the CMakeCache file
            os.remove('CMakeCache.txt')
        except OSError:
            # file does not exist -> no problem
            pass
    else:
        raise RuntimeError("Error: (clean_cmake_cache) Not in build dir. "
                           "Exiting before doing some nonesense ...")

#----------------------------------------------------------------------
def create_solution(project_directory, arch, build_types, prj_build_config):
    """
    create_solution
    """
    build_type = build_types[0]
    print_verbose("create_solution")
    additional_params = prj_build_config.get('additional_params', [])

    if opt_dryrun:
        print_flush("dryrun: create solution")
        return

    if not is_valid_build_dir():
        raise RuntimeError("Error: (create_solution) Not in build dir. "
                    " Exiting before doing some nonsense ...")

    if not os.path.exists(os.path.join(project_directory, 'CMakeLists.txt')):
        raise RuntimeError("Error: No CMakeLists.txt in project dir: %s" % project_directory)


    cmake_vs_gen = CMakeVsGenerator(arch, prj_build_config)

    cmake_args = ['cmake',
                    '-DCMAKE_BUILD_TYPE=%s' % build_type,
                    project_directory] + cmake_vs_gen.get_cmake_args() + additional_params

    print_verbose(' '.join(cmake_args))

    subprocess.check_call(cmake_args)



#----------------------------------------------------------------------
def create_jom_makefile(arch, build_types, additional_params):
    """
    create_jom_makefile
    """
    build_type = build_types[0]
    print_verbose("create_jom_makefile")
    if opt_dryrun:
        print_flush("dryrun: create jom makefile")
        return
    if is_valid_build_dir():
        if os.path.exists(os.path.join('..', 'CMakeLists.txt')):
            check_cmake()
            if arch == ARCH_X86:
                subprocess.check_call(['cmake',
                                       '-DCMAKE_BUILD_TYPE=%s' % build_type,
                                       '-G', 'NMake Makefiles JOM',
                                       '..'] + additional_params)
            elif arch == ARCH_X64:
                subprocess.check_call(['cmake',
                                       '-DCMAKE_BUILD_TYPE=%s' % build_type,
                                       '-G', 'NMake Makefiles JOM Win64',
                                       '..'] + additional_params)
        else:
            raise RuntimeError("Error: No CMakeLists.txt in parent dir: %s" % os.path.abspath('..'))
    else:
        raise RuntimeError("Error: (create_solution) Not in build dir. "
                           "Exiting before doing some nonsense ...")

#----------------------------------------------------------------------
def create_ninja_makefile(project_directory, arch, build_types, additional_params):
    """
    create_ninja_makefile
    """
    build_type = build_types[0]
    print_verbose("create_ninja_makefile")
    if opt_dryrun:
        print_flush("dryrun: create ninja makefile")
        return
    if is_valid_build_dir():
        if os.path.exists(os.path.join('..', 'CMakeLists.txt')):
            check_cmake()
            if arch == ARCH_X86:
                subprocess.check_call(['cmake',
                                       '-DCMAKE_BUILD_TYPE=%s' % build_type,
                                       '-G', 'Ninja',
                                       project_directory] + additional_params)
            elif arch == ARCH_X64:
                subprocess.check_call(['cmake',
                                       '-DCMAKE_BUILD_TYPE=%s' % build_type,
                                       '-G', 'Ninja',
                                       project_directory] + additional_params)
        else:
            raise RuntimeError("Error: No CMakeLists.txt in parent dir: %s" % os.path.abspath('..'))
    else:
        raise RuntimeError("Error: (create_solution) Not in build dir. "
                           "Exiting before doing some nonsense ...")

#----------------------------------------------------------------------
def create_makefile(arch, build_type, additional_params):
    """
    create_makefile
    """
    print_verbose("create_makefile")
    if opt_dryrun:
        print_flush("dryrun: create makefile")
        return
    if is_valid_build_dir():
        if os.path.exists(os.path.join('..', 'CMakeLists.txt')):
            check_cmake()
            # allow cross compiling in Linux
            if arch == ARCH_PI:
                toolchain_file = os.path.normpath(
                    os.path.join(
                        os.path.dirname(sys.argv[0]),
                        '..',
                        'cmake',
                        'Toolchain-arm-raspberry.cmake'))
                print_flush('-DCMAKE_TOOLCHAIN_FILE=%s' % toolchain_file)
                subprocess.check_call(
                    ['cmake',
                     '-DCMAKE_TOOLCHAIN_FILE=%s' % toolchain_file,
                     '-DCMAKE_BUILD_TYPE=%s' % build_type,
                     '-DBUILD_ARCH=%s' % arch,
                     '..'] + additional_params)
            else:
                subprocess.check_call(
                    ['cmake',
                     '-DCMAKE_BUILD_TYPE=%s' % build_type,
                     '-DBUILD_ARCH=%s' % arch,
                     '..'] + additional_params)
        else:
            raise RuntimeError("Error: No CMakeLists.txt in parent dir: %s" % os.path.abspath('..'))
    else:
        raise RuntimeError("Error: (create_makefile) Not in build dir. "
                           "Exiting before doing some nonsense ...")


#----------------------------------------------------------------------
def create_xcode(project_directory, arch, build_type, additional_params):
    """
    create_xcode
    """
    print_verbose("create_xcode")
    if opt_dryrun:
        print_flush("dryrun: create xcode")
        return
    if is_valid_build_dir():
        if os.path.exists(
                os.path.join(
                    project_directory,
                    'CMakeLists.txt')):
            check_cmake()
            subprocess.check_call(
                ['cmake',
                 '-DCMAKE_BUILD_TYPE=%s' % build_type,
                 '-G', 'Xcode',
                 '-DBUILD_ARCH=%s' % arch,
                 project_directory] + additional_params)
        else:
            raise RuntimeError("Error: No CMakeLists.txt in project dir: %s" % project_directory)
    else:
        raise RuntimeError("Error: (create_xode) Not in build dir. "
                           "Exiting before doing some nonsense ...")

def get_ms_build_bin():
    """
    should be extended using vswhere for VS2017 and later
    """
    msbuild_candidates = [
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Professional/MSBuild/Current/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Professional/MSBuild/Current/Bin/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/MSBuild/Current/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/MSBuild/Current/Bin/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/MSBuild/15.0/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/MSBuild/15.0/Bin/MSBuild.exe",
        "C:/Program Files (x86)/MSBuild/12.0/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/MSBuild/12.0/Bin/MSBuild.exe"
    ]

    for msbuild in msbuild_candidates:
        if os.path.exists(msbuild):
            return msbuild

    return None

#----------------------------------------------------------------------
def build_msbuild(build_types, target):
    """
    build_msbuild
    """
    print_verbose("build_msbuild %s" % os.getcwd())
    if opt_dryrun:
        print_flush("dryrun: build_msbuild")
        return True

    ms_build_bin = get_ms_build_bin()
    if ms_build_bin is None:
        raise RuntimeError("Error: Could not find a valid MSBuild.exe installation")

    if is_valid_build_dir():
        if target is None:
            solution = None
            files = os.listdir(".")
            for solution_file in files:
                if re.match(".*sln$", solution_file) != None:
                    solution = solution_file
                    break

            if solution:
                for build_type in build_types:
                    subprocess.check_call(
                        [ms_build_bin,
                         solution,
                         '-p:Configuration=%s' % build_type,
                         '-maxcpucount',
                         '-nologo',
                         '-verbosity:minimal'])
            else:
                raise RuntimeError("Error: (build_msbuild) no solution found")
        else:
            for build_type in build_types:
                if os.path.exists(target[0] + '.vcxproj'):
                    subprocess.check_call(
                        [ms_build_bin,
                         target[0] + '.vcxproj',
                         '-p:Configuration=%s' % build_type,
                         '-maxcpucount',
                         '-nologo',
                         '-verbosity:minimal'])
                else:
                    raise RuntimeError("Error: No target %s exists in "
                                       "build dir" % (target[0] + '.vcxproj'))
    else:
        raise RuntimeError("Error: (build_msbuild) Not in build dir. "
                           "Exiting before doing some nonsense ...")
    return True


#----------------------------------------------------------------------
def build_make(target):
    """
    build_make
    """
    print_verbose("build_make")
    if opt_dryrun:
        print_flush("dryrun: build_make")
        return
    if is_valid_build_dir():
        if target != None:
            subprocess.check_call(
                ['make',
                 '-j4',
                 target[0]])
        else:
            subprocess.check_call(
                ['make',
                 '-j4'])
    else:
        raise RuntimeError("Error: (build_make) Not in build dir. "
                           "Exiting before doing some nonsense ...")

#----------------------------------------------------------------------
def build_cmake(target, build_type=None):
    """
    Start a build using cmake
    Usage: cmake --build <dir> [options] [-- [native-options]]
    Options:
    <dir>          = Project binary directory to be built.
    --target <tgt> = Build <tgt> instead of default targets.
    --config <cfg> = For multi-configuration tools, choose <cfg>.
    --clean-first  = Build target 'clean' first, then build.
                     (To clean only, use --target 'clean'.)
    --use-stderr   = Ignored.  Behavior is default in CMake >= 3.0.
    --             = Pass remaining options to the native tool.
    """
    print_verbose("build_cmake")
    if opt_dryrun:
        print_flush("dryrun: build_cmake")
        return
    if is_valid_build_dir():
        args = ['cmake', '--build', '.']

        if target != None:
            args.append('--target')
            args.append(target[0])

        if build_type != None:
            args.append('--config')
            args.append(build_type[0])

        print_verbose("build_cmake: " + args)

        subprocess.check_call(args)
    else:
        raise RuntimeError("Error: (build_cmake) Not in build dir. "
                           "Exiting before doing some nonsense ...")


#----------------------------------------------------------------------
def start_visual_studio():
    """
    start_visual_studio
    """
    print_verbose("start_visual_studio")
    if opt_dryrun:
        print_flush("dryrun: start_solution")
        return
    if is_valid_build_dir():
        # determine solution file
        solution = None
        files = os.listdir(".")
        for solution_file in files:
            if re.match(".*sln$", solution_file) != None:
                solution = solution_file
                break

        print_flush("Starting solution %s" % solution)
        if solution:
            subprocess.check_call(['start', solution], shell=True)
        else:
            raise RuntimeError("Error: (start_visual_studio) no solution found")
    else:
        raise RuntimeError("Error: (start_visual_studio) Not in build dir. "
                           "Exiting before doing some nonsense ...")


#----------------------------------------------------------------------
def start_xcode():
    """
    On OSX start the xcode project
    """
    print_verbose("start_xcode")
    if opt_dryrun:
        print_flush("dryrun: start_xcode")
        return
    if is_valid_build_dir():
        # determine xcode project
        xcodeproj = None
        files = os.listdir(".")
        for proj_file in files:
            if ".xcodeproj" in proj_file:
                xcodeproj = proj_file
                break

        print_flush("Starting Xcode %s" % xcodeproj)
        if xcodeproj:
            subprocess.check_call(['open', xcodeproj], shell=False)
        else:
            raise RuntimeError("Error: (start_xcode) no project found")
    else:
        raise RuntimeError("Error: (start_xcode) Not in build dir. "
                           "Exiting before doing some nonsense ...")

#----------------------------------------------------------------------
def main():
    """
    main function
    """
    parser = argparse.ArgumentParser(description='cmbuild.py is a script file for automated builds')
    parser.add_argument('--arch', dest='architecture',
                        action='append',
                        choices=['x86', 'x64', 'armhf' ,'pi'],
                        default=None,
                        help='Choose the architecture(s) to build for (x86 = 32bit, x64 = 64bit)')
    parser.add_argument('--build_type', '--build-type', dest='build_type',
                        action='append',
                        choices=['Debug', 'Release', 'RelWithDebInfo', 'coverage'],
                        default=None,
                        help='Set the build type(s). Debug is default')

    if sys.platform == 'win32':
        parser.add_argument('--vs_version', '--vs-version', dest='vs_version',
                            action='store',
                            choices=['2008', '2010', '2012', '2013', '2015', '2017', '2019'],
                            default=None,
                            help='Choose Visual Studio version')
        parser.add_argument('--jom', dest='jom',
                            action='store_true',
                            default=False,
                            help='Create JOM makefiles')

    parser.add_argument('--toolset', dest='cmake_toolset',
                        action='append',
                        default=[],
                        help='Specify the CMAKE_GENERATOR_TOOLSET (cmake -t)')

    parser.add_argument('--ninja', dest='ninja',
                        action='store_true',
                        default=False,
                        help='Create Ninja makefiles')
    parser.add_argument('--xcode', dest='xcode',
                        action='store_true',
                        default=False,
                        help='Create Xcode project instead of Makefile (Mac only)')

    parser.add_argument('-s', '--start-solution', dest='start_solution',
                        action='store_true',
                        default=False,
                        help='Command: Start Visual Studio')

    parser.add_argument('-m', '--make', dest='make',
                        action='store_true',
                        default=False,
                        help='Command: Build the project always using cmake to create makefile or msbuild')

    parser.add_argument('--make-fast', dest='make_fast',
                        action='store_true',
                        default=False,
                        help='Command: Build the project without using cmake before (faster but unsafe)')

    parser.add_argument('-t', '--target', dest='target',
                        action='append',
                        default=None,
                        help='In combination with --make use the given value as build target')

    parser.add_argument('--builddir', dest='builddir',
                        action='store',
                        default=None,
                        help='Used to override the build directory')

    parser.add_argument('--clean-cache', dest='clean_cache',
                        action='store_true',
                        default=True,
                        help='Always delete CMakeCache.txt (default)')

    parser.add_argument('--no-clean-cache', dest='clean_cache',
                        action='store_false',
                        help='Do not delete CMakeCache.txt')

    parser.add_argument('--no-regen', dest='no_regeneration',
                        action='store_true',
                        default=False,
                        help='Project files will not automatically regenerate   '
                             'after changes in CMakeList.txt files.')

    parser.add_argument('--dryrun', dest='dryrun',
                        action='store_true',
                        default=False,
                        help='Simulate build')

    parser.add_argument('--graph', dest='graph',
                        action='store_true',
                        default=False,
                        help='Generate dependency graph (no solution will be generated)')

    parser.add_argument('-D', dest='defines',
                        action='append',
                        default=[],
                        help='Define Vars')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        default=False,
                        help='Be more verbose')

    # support non-option "--" which causes all following positional
    # parameters to end up in cmake_args
    parser.add_argument('cmake_args', nargs='*',
                        help='Any additional parameters for cmake '
                             '(for example  "cmbuild -- --graphviz=test.dot")')

    args = parser.parse_args()

    # Set defaults manually as argparse does not remove defaults from the cmdline
    # as it should when ussing append action
    if args.architecture is None:
        args.architecture = DEFAULT_ARCH
    if args.build_type is None:
        args.build_type = DEFAULT_BUILD

    global opt_dryrun
    opt_dryrun = args.dryrun
    global opt_verbose
    opt_verbose = args.verbose

    project_directory = os.getcwd()

    # remove duplicates
    args.architecture = list(set(args.architecture))
    args.build_type = list(set(args.build_type))

    try:
        # let's build
        for arch in args.architecture:
            bdir = BuildDir(arch, args.builddir)
            bdir.create_build_dir()
            bdir.change_to_build_dir()

            if args.clean_cache:
                clean_cmake_cache()

            additional_params = []
            if args.no_regeneration:
                additional_params += ["-DCMAKE_SUPPRESS_REGENERATION:BOOL=1"]
            for defstr in args.defines:
                additional_params += ["-D" + defstr]

            if args.graph:
                additional_params += [r"--graphviz=_graph\oxy"]

            additional_params = additional_params + args.cmake_args

            args.cmake_toolset = args.cmake_toolset[-1:]

            prj_build_config = {
                "cmake_toolset" : args.cmake_toolset,
                "additional_params" : additional_params
            }

            # windows only parts:
            if sys.platform == 'win32':
                if not args.jom and not args.ninja:
                    vs_version = {
                        '2008' : '9',
                        '2010' : '10',
                        '2012' : '11',
                        '2013' : '12',
                        '2015' : '14',
                        '2017' : '15',
                        '2019' : '16',
                        }.get(args.vs_version, DEFAULT_STUDIO_VERSION)

                    prj_build_config.update({
                        'vs_version' : vs_version
                    })

                    # try to build wo running cmake for "fast" configurations                   
                    build_success = False
                    if args.make_fast:
                        try:
                            build_success = build_msbuild(args.build_type, args.target)
                        except RuntimeError as error:
                            build_success = False

                    if not build_success:
                        create_solution(
                            project_directory,
                            arch,
                            args.build_type,
                            prj_build_config)

                        if args.start_solution:
                            start_visual_studio()

                        if args.make:
                            build_msbuild(args.build_type, args.target)

                elif args.jom:
                    create_jom_makefile(
                        arch,
                        args.build_type,
                        additional_params)
                elif args.ninja:
                    create_ninja_makefile(
                        project_directory,
                        arch,
                        args.build_type,
                        additional_params)
                else:
                    print_flush("Unknown build type")
                    return 1


            # linux only parts:
            if 'linux' in sys.platform:
                if args.ninja:
                    create_ninja_makefile(
                        project_directory,
                        arch,
                        args.build_type,
                        additional_params)
                else:
                    create_makefile(
                        arch,
                        args.build_type[0],
                        additional_params)
                    if args.make:
                        build_cmake(args.target)

            # Darwin -> MacOS
            if 'darwin' in sys.platform:
                if args.xcode:
                    create_xcode(
                        project_directory,
                        arch,
                        args.build_type[0],
                        additional_params)
                    if args.start_solution:
                        start_xcode()
                else:
                    create_makefile(
                        arch,
                        args.build_type[0],
                        additional_params)
                if args.make:
                    build_cmake(args.target)

    except Exception as error:
        print_flush(error)
        return 1

    return 0

#----------------------------------------------------------------------
# main
if __name__ == "__main__":
    sys.exit(main())

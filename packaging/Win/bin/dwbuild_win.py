#! python

#
# dwbuild.win.py Copyright (c) Dewetron 2015
#
# TASKS:
# - build projects
# - install projects
# - build MSI files (Windows Installers)
# - Deploy MSI files
# - Build Installer Bundle (all-in-one)


import argparse
import ctypes
from copy import deepcopy
from distutils.dir_util import copy_tree
import itertools
import glob
import json
import platform
import os
import re
import subprocess
import shutil
import string
import tempfile
import glob
import fnmatch
from pprint import pprint
import zipfile

import sys
sys.path.append('packaging/win/bin')
from dwsign import dwsign
from dwmsi import dwmsi


VERBOSE = 0

PYTHON_COMMAND = sys.executable
PACKAGE_BUILD_DIR = None

# guess package dir
PACKAGE_CONFIG_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(sys.argv[0]), '..'))
REPOSITORY_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(sys.argv[0]), '..', '..', '..'))


def die(msg):
    print("-----------------------------------------------------------------")
    print("dwbuild: Error: %s" % msg, flush=True)
    sys.exit(1)


def verbose(msg):
    if VERBOSE:
        print('dwbuild:', msg, flush=True)


def debug(msg):
    print("dwbuild: DEBUG: %s" % (msg), flush=True)


def removeFilesRecursive(build_dir, patterns):
    """
    build_dir
    patterns
    """
    matches = []
    for root, _, filenames in os.walk(build_dir):
        for pattern in patterns:
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))

    for mf in matches:
        try:
            os.remove(mf)
        except:
            pass


def get_dwbuild_config():
    """
    get_dwbuild_config JSON configuration
    """
    global REPOSITORY_ROOT

    # process json build config
    build_config_path = os.path.join(
        REPOSITORY_ROOT, 'packaging', 'Win', 'dwbuild_config', 'dwbuild_config.json')

    with open(build_config_path) as f:
        build_configurations = json.load(f)

    # pprint(build_configurations)

    return build_configurations


def get_build_dir(arch):
    """
    get_build_dir
    """
    build_dir = 'build'
    if arch == 'x86':
        return build_dir
    if arch == 'x64':
        return build_dir + '64'
    if arch == None:
        return build_dir
    return build_dir + arch


def get_ms_build_bin():
    """
    should be extended using vswhere for VS2017 and later
    """
    msbuild_candidates = [
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Professional/MSBuild/Current/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Professional/MSBuild/Current/Bin/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/MSBuild/15.0/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional/MSBuild/15.0/Bin/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/MSBuild/Current/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/MSBuild/Current/Bin/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2017/Community/MSBuild/15.0/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/Microsoft Visual Studio/2017/Community/MSBuild/15.0/Bin/MSBuild.exe",
        "C:/Program Files (x86)/MSBuild/12.0/Bin/amd64/MSBuild.exe",
        "C:/Program Files (x86)/MSBuild/12.0/Bin/MSBuild.exe"
    ]

    for msbuild in msbuild_candidates:
        if os.path.exists(msbuild):
            return msbuild

    return None


def get_inf2cat_bin():
    """
    look for a valid inf2cat.exe
    """
    inf2cat_candidates = [
        "C:/Program Files (x86)/Windows Kits/10/bin/x86/Inf2Cat.exe"
    ]

    for inf2cat in inf2cat_candidates:
        if os.path.exists(inf2cat):
            return inf2cat

    return None


def get_version(version_file):
    """
    get_version
    """
    version_keys = [ 'VERSION_MAJOR', 'VERSION_MINOR', 'VERSION_MICRO' ]

    f = open(version_file)

    version = ""

    for line in f:
        for vk in version_keys:
            match = re.search(r'^#define\s+%s\s+(.*)' % vk, line)
            if match is not None:
                ver = match.group(1).strip()
                version += ver + '.'
                break

    if version != "":
        version = version[:-1]

    return version


def get_setup_name(prj_build_cfg, cbc, arch = None):
    """
    get_setup_name(prj_build_cfg, cbc, arch = None)
    """
    assert not isinstance(arch, (list,)), "arch should not be a list here"
    if arch == None:
        if cbc != None:
            arch = cbc.get('arch', None)
            if arch == None:
                arch = prj_build_cfg.get('arch', None)
        else:
            arch = prj_build_cfg.get('arch', None)

    setup_name = prj_build_cfg.get('setup_name', None)
    if setup_name == None and cbc != None:
        setup_name = cbc.get('setup_name', None)
            
    version = None
    if cbc != None:
        version_file = cbc.get('version_file', None)
        if version_file:
            version = get_version(version_file)
            revision = prj_build_cfg.get('revision', None)
            if revision:
                version = version + "." + revision

    #assert setup_name != None, "setup_name must not be None"
    if setup_name != None:
        setup_name = setup_name.replace("%ARCH%", arch)
        if version:
            setup_name = setup_name.replace("%VERSION%", version)
    else:
        setup_name = prj_build_cfg.get('name', None)
    return setup_name


# ----------------------------------------------------------------------
# for valid_types refer to GetDriveType MSDN doc (default: fixed + network)
def GetAvailableDrives(valid_types=[3, 4]):
    if 'Windows' not in platform.system():
        return []
    drive_bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
    all_drive_letters = list(itertools.compress(string.ascii_uppercase, map(
        lambda x: ord(x) - ord('0'), bin(drive_bitmask)[:1:-1])))
    print("all_drive_letters are %s" % (all_drive_letters))
    valid_drives = []
    for drive_letter in all_drive_letters:
        drive_path = drive_letter+":\\"
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
        if drive_type in valid_types:
            valid_drives = valid_drives + [drive_path]
    return valid_drives

# ----------------------------------------------------------------------


def FindValidPath(drives, paths):
    for drive in drives:
        for path in paths:
            #print ("checking " + drive+path)
            if os.path.isdir(drive+path):
                return [drive, path]
    return ["", ""]


def get_pkg_version():
    """
    Try to guess the software version of the package
    """
    if os.path.exists(os.path.join('version_info', 'MajorVersion.h')):
        version_file = open(os.path.join('version_info', 'MajorVersion.h'))
        for line in version_file:
            if 'MAJOR' in line:
                print(line)
            if 'MINOR' in line:
                print(line)


# Build the project
def _cmbuild(arch, build_type, additional_params):
    """
    Wrap function for calling cmbuild
    """
    global REPOSITORY_ROOT
    cm_build_path = os.path.join(
        REPOSITORY_ROOT, 'build_util', 'bin', 'cmbuild.py')

    verbose("_cmbuild %s %s %s" % (arch, build_type, additional_params))

    if os.path.exists(cm_build_path):
        try:
            subprocess.check_call([PYTHON_COMMAND, cm_build_path,
                                   '-v',
                                   '--arch=%s' % (arch),
                                   '--build_type=%s' % (build_type),
                                   '--make'] + additional_params)

            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                'cmbuild problem (CalledProcessError) (%s)' % str(e))
    return False


def get_install_dir(prj_build_cfg, cbc):
    """
    get_install_dir
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    if cbc:
        install_dir = cbc.get('install_dir', None)
        install_prefix = prj_build_cfg.get('install_prefix', None)
        assert install_prefix != None, "install_prefix has to be set"

        # extend install_prefix with name
        if install_dir:
            install_prefix = os.path.join(install_prefix, install_dir)
        else:
            install_prefix = os.path.join(install_prefix, name)

        return install_prefix
    return ""


def build(module, pkg_build_dir, install_prefix, arch, build_type, prj_build_cfg, additional_params):
    """
    Build a project
    """
    cwd = os.getcwd()
    verbose("build %s %s %s" % (module, arch, build_type))

    pkg_build_dir_l = os.path.normpath(os.path.join(cwd, pkg_build_dir))
    verbose("in directory:%s" % pkg_build_dir_l)

    build_dir = prj_build_cfg.get("build_dir", None)
    if build_dir:
        additional_params = additional_params + ["--builddir=%s" % build_dir]

    vs_version = prj_build_cfg.get("vs_version", None)
    if vs_version:
        additional_params = additional_params + ["--vs-version=%s" % vs_version]
    toolset = prj_build_cfg.get("cmake_toolset", None)
    if toolset:
        additional_params = additional_params + ["--toolset=%s" % toolset]

    additional_params = additional_params + ["-DCMAKE_INSTALL_PREFIX=%s" % (install_prefix)]

    if os.path.exists(pkg_build_dir_l):
        os.chdir(pkg_build_dir_l)
        if not _cmbuild(arch, build_type, additional_params):
            return False
        os.chdir(cwd)
        return True
    else:
        verbose("folder not found")
    return False


def build_from_json(prj_build_cfg, build_configurations):
    """
    build_from_json
    Gets the build configuration and triggers following commands depending on
    the package individual configuration:
        - build the project
        - install artifacts to a defined intermediate directory
        - create an installer using the build artifacts.
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    prj_arch = prj_build_cfg.get('arch', None)

    cbc = build_configurations[name]
    if cbc:
        project_list_arch = project_list = None
        if prj_arch != None:
            project_list_arch = cbc.get('project_list_%s' % prj_arch, None)
        if project_list_arch != None:
            project_list = project_list_arch
        else:
            project_list = cbc.get('project_list', None)

        install = cbc.get('install', False)
        catalog = cbc.get('catalog', False)
        cabinet = cbc.get('cabinet', False)
        extract = cbc.get('extract', False)
        msi = cbc.get('msi', False)
        archive = prj_build_cfg.get('create_zip', False)

        if project_list:
            #verbose("build_from_json unpacking project_list for %s" % (PACKAGE))
            for prj in project_list:
                child_prj_build_cfg = deepcopy(prj_build_cfg)
                child_prj_build_cfg['name'] = prj

                success = build_from_json(child_prj_build_cfg, build_configurations)
                if not success:
                    return False
           
            if install:
                if not install_from_json_this(prj_build_cfg, build_configurations):
                    return False

            if msi:
                # determine if subprojects artifacts should be copied together
                # usually a prestep for msi generation
                merge_project_artefacts(project_list, prj_build_cfg, build_configurations)

            if archive:
                if not create_archive_from_json(prj_build_cfg, build_configurations):
                    return False

            if catalog:
                if not create_catalog_from_json(prj_build_cfg, build_configurations):
                    return False

            if cabinet:
                if not create_cabinet_from_json(prj_build_cfg, build_configurations):
                    return False

            if extract:
                if not extract_driver_from_json(prj_build_cfg, build_configurations):
                    return False

            if msi:
                skip_msi = prj_build_cfg.get('skip_msi', False)
                if not skip_msi:
                    if not create_installer_from_json(prj_build_cfg, build_configurations):
                        return False



            sign = not prj_build_cfg.get('skip_sign', True)
            if sign and msi:
                if not sign_package(prj_build_cfg, build_configurations):
                    return False
    
            deploy = not prj_build_cfg.get('skip_deploy', True)
            if deploy and msi:
                if not deploy_from_json(prj_build_cfg, build_configurations):
                    return False
        else:
            verbose("build_from_json building project %s" % (name))
            additional_params = prj_build_cfg.get('additional_params', [])
            build_type = prj_build_cfg.get('build_type', None)
            archive = prj_build_cfg.get('create_zip', False)

            arch = cbc.get('arch', None)
            if arch == None:
                arch = prj_build_cfg.get('arch', None)

            project_dir = cbc.get('project_dir', None)

            install_prefix = get_install_dir(prj_build_cfg, cbc)

            args = cbc.get('args', None)
            skip = project_dir is None or cbc.get('skip_build', False) or prj_build_cfg.get('skip_build', False)
            
            if args:
                add_args = additional_params + args
            else:
                add_args = additional_params


            if not skip:                
                if not build(name, project_dir, install_prefix, arch, build_type, prj_build_cfg, add_args):
                    return False
            else:
                verbose("build_from_json %s skipped" % (name))

            if install:
                if not install_from_json(prj_build_cfg, build_configurations):
                    return False

            if archive:
                if not create_archive_from_json(prj_build_cfg, build_configurations):
                    return False

            if extract:
                if not extract_driver_from_json(prj_build_cfg, build_configurations):
                    return False

            if msi:
                if not create_installer_from_json(prj_build_cfg, build_configurations):
                    return False

            sign = not prj_build_cfg.get('skip_sign', True)
            if sign and msi:
                if not sign_package(prj_build_cfg, build_configurations):
                    return False
        
            deploy = not prj_build_cfg.get('skip_deploy', True)
            if deploy and msi:
                if not deploy_from_json(prj_build_cfg, build_configurations):
                    return False

        return True
    return False


def build_project(prj_build_cfg):
    """
    Build a project and other projects needed
    """
    build_configurations = get_dwbuild_config()

    # build from json
    name = prj_build_cfg.get('name', None)
    if name in build_configurations.keys():
        return build_from_json(prj_build_cfg, build_configurations)

    # try building projects not mentioned in json configuration
    arch = prj_build_cfg.get('arch', 'x64')
    project_dir = prj_build_cfg.get('project', None)
    build_type = prj_build_cfg.get('build_type', 'Release')
    additional_params = prj_build_cfg.get('additional_params', [])
    install_prefix = prj_build_cfg.get('install_prefix', None)
    # extend install_prefix with name
    install_prefix = os.path.join(install_prefix, name)

    package_config_base_dir = prj_build_cfg.get('package_config_base_dir', None)

    skip_build = prj_build_cfg.get('skip_build', False)
    skip_install = prj_build_cfg.get('skip_install', False)
    skip_msi = prj_build_cfg.get('skip_msi', False)
    skip_sign = prj_build_cfg.get('skip_sign', False)
    skip_deploy = prj_build_cfg.get('skip_deploy', False)

    build_dir = prj_build_cfg.get("build_dir", None)

    assert project_dir != None, "project_dir must not be None"

    if not skip_build:
        if not build(name, project_dir, install_prefix, arch, build_type, prj_build_cfg, additional_params):
            return False
    if not skip_install:
        if not install(name, project_dir, install_prefix, package_config_base_dir, build_dir, arch, build_type, False):
            return False
    if not skip_msi:
        if not create_installer(prj_build_cfg):
            return False
    if not skip_sign:
        if not sign_package(prj_build_cfg):
            return False
    if not skip_deploy:
        if not deploy_from_json(prj_build_cfg, build_configurations):
            return False
    return True


def install_msbuild(vxcproj_path, build_type, arch):
    """
    make install using msbuild
    """
    global REPOSITORY_ROOT
    verbose("install_msbuild vxcproj_path=%s, build_type=%s, arch=%s" %
            (vxcproj_path, build_type, arch))

    ms_build_bin = get_ms_build_bin()
    if ms_build_bin is None:
        raise RuntimeError("Error: Could not find a valid MSBuild.exe installation")

    if os.path.exists(vxcproj_path):
        os.chdir(vxcproj_path)
        subprocess.check_call([ms_build_bin, 'INSTALL.vcxproj', '-p:Configuration=%s;Platform=%s' %
                               (build_type, arch), '-nologo', '-verbosity:minimal'])
        os.chdir(REPOSITORY_ROOT)
    else:
        raise RuntimeError(
            "Error:    no BUILD directory found: %s" % (vxcproj_path))

# TODO maybe split in subroutines instead of: if elif ...


def install_filecopy(srcpath, dstpath, filelist):
    """
    install_filecopy
    """
    wildcard_file = 0
    wildcard_dir = 0
    wildcard_file_type = 0

    if not os.path.exists(dstpath):
        verbose("Create Directory %s" % (dstpath))
        os.makedirs(dstpath)

    for fn in filelist:
        # file wildcard?
        if fn.find("*.*") != -1:
            verbose("INFO: File wildcard found")
            wildcard_file = 1
            break
        # directory wildcard?
        elif fn.find("* *") != -1:
            verbose("INFO: Directory wildcard found")
            wildcard_dir = 1
            break
        # file type wildcard?
        elif fn.find("*.") != -1:
            verbose("INFO: File Type wildcard found")
            wildcard_file_type = 1
            pattern = fn[1:]
            verbose("-------->:%s:" % pattern)
            break

    # Copy ALL FILES
    if wildcard_file:
        src_dir = os.path.normcase(os.path.join(srcpath, "*"))
        for fn in glob.glob(src_dir):
            if fn.find(".") != -1 and not os.path.isdir(fn):
                shutil.copy(fn, dstpath)

    # Copy A WHOLE DIRECTORY
    elif wildcard_dir:
        if os.path.exists(dstpath):
            shutil.rmtree(dstpath)
        shutil.copytree(srcpath, dstpath)

    # Copy ALL FILES with specific type
    elif wildcard_file_type:
        src_dir = os.path.normcase(os.path.join(srcpath, "*%s") % (pattern))
        verbose('install_filecopy %s' %src_dir)
        for fn in glob.glob(src_dir):
            if fn.find(".") != -1:
                shutil.copy(fn, dstpath)

    # Copy normal
    else:
        verbose("INFO: Copy normal: %s" % (fn))
        for fn in filelist:
            sf = os.path.join(srcpath, fn)
            df = os.path.join(dstpath, fn)
            if os.path.exists(sf):
                shutil.copyfile(sf, df)
            else:
                raise RuntimeError("Error: %s does not exist" % (sf))


def install(PACKAGE, project_dir, install_prefix, package_base_path, build_dir, arch, build_type, skip_msbuild_install):
    """
    install
    """
    verbose("install %s %s %s %s" % (PACKAGE, project_dir, arch, build_type))

    if arch != None:
        if build_dir:
            exec_install = os.path.normcase(build_dir)
        else:
            exec_install = os.path.normcase(
                os.path.join(project_dir, get_build_dir(arch)))

        # bundles do not have CMake
        if not skip_msbuild_install:
            # CMake "Install" rule
            install_msbuild(exec_install, build_type, arch)

    # Copy packaging/Win/apps/[xxx] stuff
    # Hint *.wxs
    src = os.path.join(package_base_path, project_dir)
    verbose("install other: %s %s %s" % (src, install_prefix, '*.*'))
    install_filecopy(src, install_prefix, ['*.*'])
    return True


def install_from_json(prj_build_cfg, build_configurations):
    """
    install_from_json
    Calls the projects install rule
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations[name]
    if cbc:
        project_list = cbc.get('project_list', None)
        if project_list:
            #verbose("install_from_json unpacking project_list for %s" % (PACKAGE))
            for prj in project_list:
                child_prj_build_cfg = deepcopy(prj_build_cfg)
                child_prj_build_cfg['name'] = prj

                success = install_from_json(child_prj_build_cfg, build_configurations)
                if not success:
                    return False
        else:
            return install_from_json_this(prj_build_cfg, build_configurations)            

        return True
    return False


def install_from_json_this(prj_build_cfg, build_configurations):
    """
    install_from_json_this
    Calls the projects install rule
    Do not walk "project_list"
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations[name]
    if cbc:
        verbose("install_from_json_this installing project %s" % (name))
        build_type = prj_build_cfg.get('build_type', None)
        install_prefix = prj_build_cfg.get('install_prefix', None)
        # extend install_prefix with name
        install_prefix = os.path.join(install_prefix, name)

        package_config_base_dir = prj_build_cfg.get('package_config_base_dir', None)
        build_dir = prj_build_cfg.get("build_dir", None)

        arch_list = []
        arch = cbc.get('arch', None)
        if arch == None:
            arch = prj_build_cfg.get('arch', None)

        if isinstance(arch, (list,)):
            arch_list = arch
        else:
            arch_list = [arch]

        for arch in arch_list:
            project_dir = cbc.get('project_dir', None)
            bundle = cbc.get('bundle', False)
            skip_msbuild_install = cbc.get('skip_msbuild_install', False) or prj_build_cfg.get('skip_msbuild_install', False)
            skip = project_dir is None or cbc.get('skip_install', False) or prj_build_cfg.get('skip_install', False)

            if not skip:
                return install(name, project_dir, install_prefix, package_config_base_dir, build_dir, arch, build_type, bundle or skip_msbuild_install)
            else:
                verbose("install_from_json_this %s skipped" % (name))
        return True
    return False


def merge_project_artefacts(project_list, prj_build_cfg, build_configurations):
    """
    merge_project_artefacts
    Gather the artefacts of multiple projects into a common directory    
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"
  
    skip = prj_build_cfg.get('skip_merge', False)
    if skip:
        verbose("merge_project_artefacts %s %s skipped" %(name, project_list))
        return

    verbose("merge_project_artefacts %s %s" %(name, project_list))
    # all child projects must have the same install_prefix
    install_prefix = prj_build_cfg.get('install_prefix', None)
    dest_install_dir = os.path.join(install_prefix, name)

    for prj in project_list:
        prj_install_prefix = os.path.join(install_prefix, prj)
        copy_tree(prj_install_prefix, dest_install_dir)


def clean(module, pkg_build_dir, arch, build_type):
    """
    Clean temporaries of a project
    """
    verbose("clean %s %s %s" % (module, pkg_build_dir, arch))

    cwd = os.getcwd()
    pkg_build_dir_l = os.path.normpath(os.path.join(cwd, pkg_build_dir))
    verbose("in directory:%s" % pkg_build_dir_l)

    if os.path.exists(pkg_build_dir_l):
        os.chdir(pkg_build_dir_l)
        build_dir = get_build_dir(arch)
        removeFilesRecursive(build_dir, ['*.obj', '*.lib'])

        os.chdir(cwd)
        return True
    else:
        verbose("folder not found")
    return False


def clean_from_json(prj_build_cfg, build_configurations):
    """
    clean_from_json
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations[name]
    if cbc:
        project_list = cbc.get('project_list', None)
        if project_list:
            #verbose("install_from_json unpacking project_list for %s" % (PACKAGE))
            for prj in project_list:
                child_prj_build_cfg = deepcopy(prj_build_cfg)
                child_prj_build_cfg['name'] = prj

                success = clean_from_json(child_prj_build_cfg, build_configurations)
                if not success:
                    return False
        else:
            verbose("clean_from_json project %s" % (name))
            build_type = prj_build_cfg.get('build_type', None)

            arch = cbc.get('arch', None)
            project_dir = cbc.get('project_dir', None)
            skip = project_dir is None or cbc.get('skip_clean', False) or prj_build_cfg.get('skip_clean', False)

            if not skip:
                if isinstance(arch, (list,)):
                    arch_list = arch
                else:
                    arch_list = [arch]

                for arch in arch_list:
                    clean(name, project_dir, arch, build_type)
            else:
                verbose("clean_from_json %s skipped" % (name))

        return True
    return False


def clean_build(prj_build_cfg):
    """
    Cleanup temporaries and build artefacts
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    build_configurations = get_dwbuild_config()

    if name in build_configurations.keys():
       return clean_from_json(prj_build_cfg, build_configurations)

    return True


def create_installer_from_json(prj_build_cfg, build_configurations):
    """
    create_installer_from_json (usually a msi using wix toolset)
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations[name]
    if cbc:
        # arch preferable set by json cfg
        arch = cbc.get('arch', None)
        if isinstance(arch, (list,)):
            for arch_t in arch:
                print("arch = %s" % arch_t, flush=True)
                if not create_installer_for_arch(prj_build_cfg, cbc, arch_t):
                    return False
            return True

        if arch == None:
            arch = prj_build_cfg.get('arch', None)

        return create_installer_for_arch(prj_build_cfg, cbc, arch)


def create_installer_for_arch(prj_build_cfg, cbc, arch):
    """
    create_installer_for_arch(prj_build_cfg, cbc, arch)
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"
    assert not isinstance(arch, (list,)), "arch should not be a list here"

    setup_name = get_setup_name(prj_build_cfg, cbc, arch)

    verbose("create_installer_for_arch project %s: %s (%s)" % (name, setup_name, arch))

    skip = cbc.get('skip_msi', False) or prj_build_cfg.get('skip_msi', False)
    bundle = cbc.get('bundle', False)

    if not skip:
        cwd = os.getcwd()
        install_prefix = prj_build_cfg.get('install_prefix', None)
        # extend install_prefix with name
        install_prefix = os.path.join(install_prefix, name)

        revision = prj_build_cfg.get('revision', None)
        deployment_dir = prj_build_cfg.get('deployment_dir', None)
        vs_version = prj_build_cfg.get('vs_version', None)       

        os.chdir(install_prefix)

        # build_msi.bat depends on WORKSPACE environment variable
        # that is set in jenkins jobs to repository root
        if 'WORKSPACE' not in os.environ.keys():
            os.environ['WORKSPACE'] = REPOSITORY_ROOT

        dwmsi_args = [ '--arch', arch ]
        if VERBOSE:
            dwmsi_args = dwmsi_args + ['-v']
        if bundle:
            # gather msi(s) for bundle
            install_filecopy(deployment_dir, install_prefix, ['*.msi'])
            dwmsi_args = dwmsi_args + ['--bundle']
        if revision:
            dwmsi_args = dwmsi_args + ['--rev', revision]
        if vs_version:
            dwmsi_args = dwmsi_args + ['--runtime_version', 'vs%s' % vs_version]

        dwmsi_args = dwmsi_args + [ setup_name ]

        verbose(dwmsi_args)

        success = dwmsi(dwmsi_args)

        os.chdir(cwd)

        if success:
            print("Successfully created %s " % setup_name, flush=True)

        return success
    else:
        verbose("create_installer_from_json %s skipped" % (name))

    return True


def create_installer(prj_build_cfg):
    """
    create_installer (usually a msi using wix toolset)
    """
    verbose(prj_build_cfg)

    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    verbose("create_installer project %s" % (name))
    cwd = os.getcwd()
    install_prefix = prj_build_cfg.get('install_prefix', None)
    # extend install_prefix with name
    install_prefix = os.path.join(install_prefix, name)

    revision = prj_build_cfg.get('revision', None)

    # arch preferable set by json cfg
    arch = prj_build_cfg.get('arch', None)

    setup_name = get_setup_name(prj_build_cfg, None)
    assert setup_name != None, "create_installer needs a setup_name"

    os.chdir(install_prefix)

    # build_msi.bat depends on WORKSPACE environment variable
    # that is set in jenkins jobs to repository root
    if 'WORKSPACE' not in os.environ.keys():
        os.environ['WORKSPACE'] = REPOSITORY_ROOT

    dwmsi_args = [ '--arch', arch ]
    if VERBOSE:
        dwmsi_args = dwmsi_args + ['-v']
    if revision:
        dwmsi_args = dwmsi_args + ['--rev', revision]

    dwmsi_args = dwmsi_args + [ setup_name ]

    verbose(dwmsi_args)

    success = dwmsi(dwmsi_args)

    os.chdir(cwd)

    if success:
        print("Successfully created %s " % setup_name, flush=True)
    
    return success


def sign_package(prj_build_cfg, build_configurations = {}):
    """
    sign_package(prj_build_cfg)
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    verbose("sign_package project %s" % (name))

    cbc = build_configurations.get(name, None)
    if cbc:
        bundle = cbc.get('bundle', False)
        msi = cbc.get('msi', False)

        # arch preferable set by json cfg
        arch_list = []
        arch = cbc.get('arch', None)
        if isinstance(arch, (list,)):
            arch_list = arch
        else:
            arch_list = [arch]

        for arch in arch_list:
            setup_name = get_setup_name(prj_build_cfg, cbc, arch)

            install_prefix = prj_build_cfg.get('install_prefix', None)
            assert install_prefix != None, "install_prefix must be defined"
            # extend install_prefix with name
            install_prefix = os.path.join(install_prefix, name)

            if bundle:
                success = dwsign([os.path.join(install_prefix, setup_name), '--bundle'])
                if success:
                    print("Successfully signed %s " % setup_name, flush=True)
            if msi:
                success = dwsign([os.path.join(install_prefix, setup_name)])
                if success:
                    print("Successfully signed %s " % setup_name, flush=True)

    else:
        # assume msi signing
        #return dwsign([])
        return True
    return True


def deploy_from_json(prj_build_cfg, build_configurations):
    """
    deploy(prj_build_cfg)
    move/copy artefact to destination directory
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    verbose("deploy_from_json %s" % (name))

    cwd = os.getcwd()
    try:
        install_prefix = prj_build_cfg.get('install_prefix', None)
        # extend install_prefix with name
        install_prefix = os.path.join(install_prefix, name)       
        
        if not os.path.exists(install_prefix):
            die("deploy InstallPath %s missing" % install_prefix)

        deployment_dir = prj_build_cfg.get('deployment_dir', None)
        if not os.path.exists(deployment_dir):
            os.mkdir(deployment_dir)

        cbc = build_configurations.get(name, None)
        if cbc:
            bundle = cbc.get('bundle', False)
            if bundle:
                install_filecopy(install_prefix, deployment_dir, ['*.exe'])
            else:
                install_filecopy(install_prefix, deployment_dir, ['*.msi'])
                install_filecopy(install_prefix, deployment_dir, ['disk1/*.cab'])
        else:
            install_filecopy(install_prefix, deployment_dir, ['*.msi'])
            install_filecopy(install_prefix, deployment_dir, ['disk1/*.cab'])
    except:
        die("deploy for %s failed" % name)

    os.chdir(cwd)
    return True


def create_catalog_from_json(prj_build_cfg, build_configurations):
    """
    create_catalog_from_json
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations.get(name, None)
    skip_cbc = False
    if cbc:
        skip_cbc = cbc.get('skip_catalog', False)
    
    skip = prj_build_cfg.get('skip_catalog', False) or skip_cbc
    if skip:
        verbose("create_catalog_from_json skipped")
        return True

    verbose("create_catalog_from_json %s" % name)

    # look for inf2cat
    inf2cat_bin = get_inf2cat_bin()
    if inf2cat_bin is None:
        raise RuntimeError("Error: Could not find a valid Inf2Cat.exe installation")

    install_prefix = prj_build_cfg.get('install_prefix', None)
    if install_prefix is None:
        return False
    install_dir = os.path.normpath(os.path.join(install_prefix, name))
    verbose("in directory:%s" % install_dir)
    
    cwd = os.getcwd()

    if os.path.exists(install_dir):
        os.chdir(install_dir)

        # clean previous generated _Win10 files upfront
        win10_gen_files = glob.glob('*_Win10.*')
        for f in win10_gen_files:
            os.remove(f)
        if os.path.exists('setup.inf'):
            os.remove('setup.inf')
        if os.path.exists('disk1'):
            shutil.rmtree('disk1')


        subprocess.check_call([inf2cat_bin, '/verbose', '/driver:.', 
            '/os:6_3_X86,7_X86,8_x86,10_X86,6_3_X64,7_X64,8_x64,10_X64,Server6_3_X64,Server8_X64,Server10_X64'])

        # sign the catalog file
        success = dwsign([os.path.join(install_prefix, name, name + '.cat'), '--type', 'driver'])
        if not success:
            print("Signing failed: %s " % (name + '.cat'), flush=True)
            return False

        # copy inf and cat file for Win10 attestation signing.
        # inf_files = glob.glob('*.inf')
        # for f in inf_files:
        #     if 'Win10' not in f and f != 'setup_Win10.inf':
        #         new_inf_name = os.path.splitext(f)[0] + '_Win10' + os.path.splitext(f)[1]
        #         shutil.copy(f, new_inf_name)

        cat_files = glob.glob('*.cat')
        for f in cat_files:
            if 'Win10' not in f:
                new_inf_name = os.path.splitext(f)[0] + '_Win10' + os.path.splitext(f)[1]
                shutil.copy(f, new_inf_name)

        os.chdir(cwd)
        return True
    else:
        verbose("folder not found")


    os.chdir(cwd)
    return False


def create_cabinet_from_json(prj_build_cfg, build_configurations):
    """
    create_cabinet_from_json
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations.get(name, None)
    skip_cbc = False
    if cbc:
        skip_cbc = cbc.get('skip_cabinet', False)

    skip = prj_build_cfg.get('skip_cabinet', False) or skip_cbc
    if skip:
        verbose("create_cabinet_from_json skipped")
        return True

    verbose("create_cabinet_from_json %s" % name)

    ddf_template = r""".OPTION EXPLICIT  ; Generate errors
.Set CabinetFileCountThreshold=0
.Set FolderFileCountThreshold=0
.Set FolderSizeThreshold=0
.Set MaxCabinetSize=0
.Set MaxDiskFileCount=0
.Set MaxDiskSize=0
.Set CompressionType=MSZIP
.Set Cabinet=on
.Set Compress=on
.Set UniqueFiles=off
;Specify file name for new cab file
.Set CabinetNameTemplate=${name}.cab
; Specify the subdirectory for the files.  
; Your cab file should not have files at the root level,
; and each driver package must be in a separate subfolder.
.Set DestinationDir=${name}
;Specify files to be included in cab file
"""
    install_prefix = prj_build_cfg.get('install_prefix', None)
    if install_prefix is None:
        return False
    install_dir = os.path.normpath(os.path.join(install_prefix, name))
    verbose("in directory:%s" % install_dir)

    cwd = os.getcwd()

    if os.path.exists(install_dir):
        os.chdir(install_dir)

        ddf_t = string.Template(ddf_template)
        ddf_c = ddf_t.safe_substitute(name=name)

        # look for inf and cat file for Win10 attestation signing.
        shutil.copy("%s.inf" % name, "%s_Win10.inf" % name)
        ddf_c = ddf_c + "%s_Win10.inf" % name  + '\n'

        cat_files = glob.glob('*Win10.cat')
        for f in cat_files:
            ddf_c = ddf_c + f + '\n'
        x86_files = glob.glob('x86/*')
        if x86_files:
            ddf_c = ddf_c + r".Set DestinationDir=%s\x86" % name + '\n'
        for f in x86_files:
            ddf_c = ddf_c + f + '\n'
        x64_files = glob.glob('x64/*')
        if x64_files:
            ddf_c = ddf_c + r".Set DestinationDir=%s\x64" % name + '\n'
        for f in x64_files:
            ddf_c = ddf_c + f + '\n'

        ddf_file = name + '.ddf'
        ddf = open(ddf_file, 'w')       
        ddf.write(ddf_c)
        ddf.close()

        subprocess.check_call(['MakeCab', '/f', ddf_file])
        
        # sign the cabinet file
        success = dwsign([os.path.join(install_prefix, name, 'disk1', name + '.cab'), '--type', 'driver10'])
        if not success:
            print("Signing failed: %s " % (name + '.cab'), flush=True)
            os.chdir(cwd)    
            return False

        os.chdir(cwd)
        return True
    else:
        verbose("folder not found")

    os.chdir(cwd)
    return False


def extract_driver_from_json(prj_build_cfg, build_configurations):
    """
    extract_driver_from_json (for Signed_xxx.zip archives)
    This extremely spezialized for updating a driver installer with
    Microsoft attestation signed drivers
    Do not use for something else!
    """    
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    ref_name = name
    cbc = build_configurations.get(name, None)
    if cbc:
        ref_name = cbc.get('name', name)

    verbose("extract_driver_from_json %s -> %s" % (name, ref_name))

    install_prefix = prj_build_cfg.get('install_prefix', None)
    if install_prefix is None:
        return False
    install_dir = os.path.normpath(os.path.join(install_prefix, name))

    deployment_dir = prj_build_cfg.get('deployment_dir', None)
    if not os.path.exists(deployment_dir):
        return False

    verbose("deployment dir: %s,  install dir %s" % (deployment_dir, install_dir))

    cwd = os.getcwd()

    if os.path.exists(deployment_dir):
        os.chdir(deployment_dir)

        seven_zip_exe = None

        if os.path.exists('drivers'):
            shutil.rmtree('drivers')

        if os.path.exists('c:/tools/7za.exe'):
            seven_zip_exe = 'c:/tools/7za.exe'
        if os.path.exists('c:/Program Files/7-Zip/7z.exe'):
            seven_zip_exe = 'c:/Program Files/7-Zip/7z.exe'

        assert seven_zip_exe != None, "7z not found"

        signed_zip_files = glob.glob("Signed*.zip")
        for sz in signed_zip_files:
            verbose([seven_zip_exe, 'x', '-y', sz])
            subprocess.check_call([seven_zip_exe, 'x', '-y', sz])

        verbose('drivers/%s' % ref_name)
        if not os.path.exists('drivers/%s' % ref_name):
            print('Error: %s/drivers/%s does not exist' % (deployment_dir, ref_name), flush=True)
            os.chdir(cwd)
            return False

        # copy drivers to wox prject dir
        copy_tree('drivers/%s' % ref_name, install_dir)

        # rename inf and catalogs -> see howto_sign_for_win10.md
        shutil.move('%s/%s_Win10.inf' % (install_dir, ref_name), '%s/%s.inf' % (install_dir, ref_name))
        shutil.move('%s/%s_Win10.cat' % (install_dir, ref_name), '%s/%s_tmp.cat' % (install_dir, ref_name))
        shutil.move('%s/%s.cat' % (install_dir, ref_name), '%s/%s_Win10.cat' % (install_dir, ref_name))
        shutil.move('%s/%s_tmp.cat' % (install_dir, ref_name), '%s/%s.cat' % (install_dir, ref_name))

        # names should now be correct for installer

        os.chdir(cwd)
        return True

    os.chdir(cwd)
    return False


def zip_dir(zip_name, tip_dir):
    """
    zip_dir
    """
    archive = zipfile.ZipFile(zip_name, mode='w', compression=zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(tip_dir):
        rel_root = os.path.relpath(root, tip_dir)
        for file in files:
            archive.write(os.path.join(root, file), os.path.join(rel_root, file))
    archive.close()


def seven_zip_dir(zip_name, tip_dir):
    """
    seven_zip_dir
    """
    seven_zip_exe = None
    if os.path.exists('c:/tools/7za.exe'):
        seven_zip_exe = 'c:/tools/7za.exe'
    if os.path.exists('c:/Program Files/7-Zip/7z.exe'):
        seven_zip_exe = 'c:/Program Files/7-Zip/7z.exe'
    subprocess.check_call([seven_zip_exe, '-y', 'a', zip_name, tip_dir])



def create_archive_from_json(prj_build_cfg, build_configurations):
    """
    create_archive_from_json
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    cbc = build_configurations[name]
    if cbc:
        archive_name = name + ".zip"
        archive_name = prj_build_cfg.get("create_zip", archive_name)

        verbose("create_archive_from_json project %s: %s" % (name, archive_name))

        install_dir = get_install_dir(prj_build_cfg, cbc)

        #zip_dir(archive_name, install_prefix)
        seven_zip_dir(archive_name, install_dir)

        return True
    return False


def show_project_tree_from_json(prj_build_cfg, build_configurations, depth):
    """
    show_project_tree_from_json
    """
    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"
    prj_arch = prj_build_cfg.get('arch', None)

    cbc = build_configurations.get(name, False)
    if cbc:
        project_list_arch = project_list = None
        if prj_arch != None:
            project_list_arch = cbc.get('project_list_%s' % prj_arch, None)
        if project_list_arch != None:
            project_list = project_list_arch
        else:
            project_list = cbc.get('project_list', None)

        arch = cbc.get('arch', None)
        if arch == None:
            arch = prj_build_cfg.get('arch', None)

        line_prefix = '--' * depth
        print("%s %s (%s)" % (line_prefix, name, arch))

        if project_list:
            for prj in project_list:
                child_prj_build_cfg = deepcopy(prj_build_cfg)
                child_prj_build_cfg['name'] = prj
                show_project_tree_from_json(child_prj_build_cfg, build_configurations, depth + 1)



def show_project_tree(prj_build_cfg):
    """
    show_project_tree
    """
    build_configurations = get_dwbuild_config()

    name = prj_build_cfg.get('name', None)
    assert name != None, "project name should never be none"

    print('Project Tree:')

    cbc = build_configurations.get(name, False)
    if cbc:
        t_prj_build_cfg = deepcopy(prj_build_cfg)
        show_project_tree_from_json(t_prj_build_cfg, build_configurations, 1)



# ----------------------------------------------------------------------
def dwbuild(argv):
    """
    function interface for dwbuild_win. to be used if imported (instead of main)
    """
    parser = argparse.ArgumentParser(
        description='%s is a script file for building DEWETRON installer packages' % sys.argv[0])
    parser.add_argument('-p', '--package', dest='package_path',
                        action='store',
                        default=None,
                        required=True,
                        help='build the package defined by the PATH')
    parser.add_argument('--package-base-dir', dest='package_config_base_dir',
                        action='store',
                        default=PACKAGE_CONFIG_BASE_DIR,
                        help='path to the base directory for msi/installer package configuration (default=%s' % (PACKAGE_CONFIG_BASE_DIR))
    parser.add_argument('--setup-name', '--setup_name', dest='setup_name',
                        action='store',
                        default=None,
                        help='override the filename of the installer to create')
    parser.add_argument('--deploy-to', dest='deploy_to',
                        action='store',
                        default='NOPATH',
                        help='Relative path to MSI files. Starting from SW_APP')
    parser.add_argument('--install-prefix', '--install_prefix', dest='install_prefix',
                        action='store',
                        default='tmp/build_dir',
                        help='Set the install prefix directory (eg CMAKE_INSTALL_PREFIX)')
    parser.add_argument('--sign', dest='sign',
                        action='store_true',
                        default=False,
                        help='sign the package (default: signing disabled)')
    parser.add_argument('--skip-prepare', dest='skip_prepare',
                        action='store_true',
                        default=False,
                        help='unused (deprecated)')
    parser.add_argument('--skip-build', dest='skip_build',
                        action='store_true',
                        default=False,
                        help='omit build step')
    parser.add_argument('--skip-install', dest='skip_install',
                        action='store_true',
                        default=False,
                        help='omit install step')
    parser.add_argument('--skip-msbuild-install', dest='skip_msbuild_install',
                        action='store_true',
                        default=False,
                        help='omit msbuild install step')
    parser.add_argument('--skip-merge', dest='skip_merge',
                        action='store_true',
                        default=False,
                        help='omit merge artefact step')
    parser.add_argument('--skip-catalog', dest='skip_catalog',
                        action='store_true',
                        default=False,
                        help='omit catalog creation step')
    parser.add_argument('--skip-cabinet', dest='skip_cabinet',
                        action='store_true',
                        default=False,
                        help='omit cabinet creation step')
    parser.add_argument('--skip-msi', dest='skip_msi',
                        action='store_true',
                        default=False,
                        help='omit msi installer build step')
    parser.add_argument('--skip-sign', dest='skip_sign',
                        action='store_true',
                        default=False,
                        help='omit sign build step')
    parser.add_argument('--skip-deploy', dest='skip_deploy',
                        action='store_true',
                        default=False,
                        help='omit deploy step')
    parser.add_argument('--skip-clean', dest='skip_clean',
                        action='store_true',
                        default=False,
                        help='omit build cleanup step')
    parser.add_argument('--skip-cmake', dest='skip_cmake',
                        action='store_true',
                        default=False,
                        help='omit cmake step if possible (faster)')
    parser.add_argument('-a', '--arch', dest='arch',
                        action='store',
                        default='x64',
                        help='Set the processor architecture')
    parser.add_argument('--rev', dest='rev',
                        action='store',
                        default='1234',
                        help='SVN/hg revision for msi bundle build')
    parser.add_argument('-bt', '--build-type', '--build_type', dest='build_type',
                        action='store',
                        default='Release',
                        help='Set the build type (Release, Debug, ...)')
    parser.add_argument('--workspace', dest='workspace',
                        action='store',
                        default=None,
                        help='Set the workspace directory')
    parser.add_argument('--dry', dest='dryrun',
                        action='store_true',
                        default=False,
                        help='dont make changes')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        default=False,
                        help='be more verbose')
    parser.add_argument('-D', dest='defines',
                        action='append',
                        default=[],
                        help='Define Variables')
    parser.add_argument('--no-clean-cache', dest='clean_cache',
                        action='store_false',
                        default='True',
                        help='Do not delete CMakeCache.txt (unsafe but faster)')
    parser.add_argument('--build-dir', dest='build_dir',
                        action='store',
                        default=None,
                        help='Set the temporary build-dir to use')
    parser.add_argument('--create-zip', dest='create_zip',
                        action='store',
                        default=None,
                        help='Zip the tip directory. Depends on option --make-dist')
    parser.add_argument('--vs-version', dest='vs_version',
                        action='store',
                        choices=['2008', '2010', '2012', '2013', '2015', '2017', '2019'],
                        default=None,
                        help='Choose Visual Studio version')
    parser.add_argument('--toolset', dest='cmake_toolset',
                        action='store',
                        default=None,
                        help='Specify the CMAKE_GENERATOR_TOOLSET (cmake -t)')
    parser.add_argument('--show-tree', dest='show_tree',
                        action='store_true',
                        default=False,
                        help='Show to tree of the projects to build')

    args = parser.parse_args(argv)

    ###################
    # workout arguments
    global VERBOSE
    VERBOSE = args.verbose
    global PACKAGE_BUILD_DIR
    PACKAGE = os.path.basename(args.package_path)

    global REPOSITORY_ROOT
    if args.workspace:
        REPOSITORY_ROOT = args.workspace


    ####################
    # prepare add_params
    additional_params = []
    for defstr in args.defines:
        additional_params += ["-D" + defstr]

    # optimize build speed - unsafe
    if args.skip_cmake:
        additional_params.append("--make-fast")
        additional_params.append("--no-clean-cache")

    # if args.install_prefix:
    #     additional_params.append('-DCMAKE_INSTALL_PREFIX=%s' % args.install_prefix),

    if not args.clean_cache:
        additional_params.append('--no-clean-cache')


    ##################
    # additional paths
    PACKAGE_BUILD_DIR = args.package_path
    if args.deploy_to.find("NOPATH") < 0:
        DEPLOYMENT_DIR = r"%s\%s" % (REPOSITORY_ROOT, args.deploy_to)
    else:
        DEPLOYMENT_DIR = os.path.join(os.getcwd(), 'PKGS')
        verbose("WARNING: Default Deploy path taken: SW_APP/PKGS")

    ########
    # Infos
    if args.dryrun:
        args.skip_build = True
        args.skip_install = True
        args.skip_msi = True
        args.skip_sign = True
        args.skip_deploy = True
        args.skip_clean = True
        args.skip_cmake = True

    if args.sign:
        args.skip_sign = False

    # fix the 2017 to 2019 & v141 support
    if args.vs_version == "2017":
        if not args.cmake_toolset:
            args.cmake_toolset = "v141"
            args.vs_version = "2019"

    # gather build configuration parameters
    prj_build_cfg = {
        "name" : PACKAGE,
        "setup_name" : args.setup_name,
        "arch" : args.arch,
        "build_type" : args.build_type,
        "revision" : args.rev,
        "additional_params" : additional_params,
        "project" : args.package_path,
        "install_prefix" : os.path.normpath(os.path.abspath(args.install_prefix)),
        "package_config_base_dir" : args.package_config_base_dir,
        "build_dir" : args.build_dir,
        "deployment_dir" : DEPLOYMENT_DIR,
        "create_zip" : args.create_zip,
        "skip_build" : args.skip_build,
        "skip_install" : args.skip_install,
        "skip_msbuild_install" : args.skip_msbuild_install,
        "skip_merge" : args.skip_merge,
        "skip_catalog" : args.skip_catalog,
        "skip_cabinet" : args.skip_cabinet,
        "skip_msi" : args.skip_msi,
        "skip_sign" : args.skip_sign,
        "skip_deploy" : args.skip_deploy,
        "skip_clean" : args.skip_clean,
        "skip_cmake" : args.skip_cmake,
        "vs_version" : args.vs_version,
        "cmake_toolset" : args.cmake_toolset
    }

    verbose("Project build info:")
    for cfg_key in prj_build_cfg.keys():
        verbose(" - %s : %s" % (cfg_key, prj_build_cfg[cfg_key]))


    ########
    if args.show_tree:
        show_project_tree(prj_build_cfg)


    #########################################
    # check if this package should be ignored
    # a 'dwgignore' signals that
    if os.path.exists(os.path.join(args.package_config_base_dir, args.package_path, 'dwignore')):
        verbose("INFO:    dwignore found - Exiting")
        return 0


    ##########################
    # build module(s)
    if not build_project(prj_build_cfg):
        die("ERROR:   STEP build %s failed" % prj_build_cfg['name'])


    ############
    # clean STEP
    if not args.skip_clean:
        verbose("INFO:    STEP clean build started")
        clean_build(prj_build_cfg)

    return True


# ----------------------------------------------------------------------
# main
if __name__ == "__main__":
    ret = dwbuild(sys.argv[1:])
    # cmdlne expexts 0 (== False) for success
    sys.exit(not ret)

#! python

#
# dwmsi.py Copyright (c) Dewetron 2019
#

import argparse
from distutils.dir_util import copy_tree
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

VERBOSE = 0
REPOSITORY_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(sys.argv[0]), '..', '..', '..'))
WIXPATH = None


# additions to candle & light commandline depending on used 
# extensions in project.wix file
WIXTOOLSET_EXTENSIONS = {
    "http://schemas.microsoft.com/wix/FirewallExtension" : {
        "candle": [ "-ext", "%WIX_PATH%/WixFirewallExtension.dll" ],
        "light": [ "-ext", "%WIX_PATH%/WixFirewallExtension.dll" ]
    },
    "http://schemas.microsoft.com/wix/DifxAppExtension" : {
        "candle": [ "-ext", "%WIX_PATH%/WixDifxAppExtension.dll" ],
        "light": [ "-ext", "%WIX_PATH%/WixDifxAppExtension.dll", "%WIX_PATH%/difxapp_%ARCH%.wixlib" ]
    },
    "http://schemas.microsoft.com/wix/UtilExtension" : {
        "candle": [ "-ext", "%WIX_PATH%/WixUtilExtension.dll" ],
        "light": [ "-ext", "%WIX_PATH%/WixUtilExtension.dll" ]
    },
    "http://schemas.microsoft.com/wix/BalExtension" : {
        "candle": [ "-ext", "%WIX_PATH%/WixBalExtension.dll" ],
        "light": [ "-ext", "%WIX_PATH%/WixBalExtension.dll" ]
    }
}


def die(msg):
    print("-----------------------------------------------------------------")
    print("Error: %s" % msg, flush=True)
    sys.exit(1)


def verbose(msg):
    if VERBOSE:
        print(msg, flush=True)


def get_wix_config_json():
    """
    get_wix_config_json():
    """
    try:
        with open('wix_config.json') as f:
            build_configurations = json.load(f)
        return build_configurations
    except:
        return {}


def copy_runtime_msm(runtime_version, arch):
    """
    copy_runtime_msm(arch, runtime_version)
    Copies VS runtime msm package into the current working directory
    The destination file name has to be 'MergeModule_xANY.msm' as by this
    it is referenced in the project.wix files.
    """
    dest_filename = 'MergeModule_xANY.msm'
    runtime_msm_source_path = os.path.normpath(os.path.join(REPOSITORY_ROOT, 'packaging/Win/bin/CPPRuntime/%s_%s' % (runtime_version, arch)))
    verbose("copy_runtime_msm: %s" % (runtime_msm_source_path))
    msm_files = glob.glob('%s/*' % (runtime_msm_source_path))
    if not msm_files:
        return False

    for f in msm_files:
        verbose("copy %s %s" % (f, dest_filename))
        shutil.copy(f, dest_filename)
    
    return True


def update_wix_extensions(wxs_file, tool):
    """
    update_wix_extensions(wxs_file):
    """
    wix_ext = []
    wxs_namespaces = dict([node for _, node in ET.iterparse(wxs_file, events=['start-ns'])])
    #print(wxs_namespaces)

    for ns_key in wxs_namespaces.keys():
        ext_name = wxs_namespaces[ns_key]
        tool_mapping = WIXTOOLSET_EXTENSIONS.get(ext_name, None)

        if tool_mapping != None:
            ext_dll_mapping = tool_mapping.get(tool, None)

            if ext_dll_mapping != None:
                wix_ext = wix_ext + ext_dll_mapping

    return wix_ext


def resolve_extension_path(wix_ext, wix_cfg):
    """
    resolve_extension_path(wix_ext, wix_cfg):
    """
    arch = wix_cfg.get('arch', None)
    wix_ext_out = []
    for ext in wix_ext:
        ext_subst = ext
        ext_subst = ext_subst.replace('%WIX_PATH%', WIXPATH)
        ext_subst = ext_subst.replace('%ARCH%', arch)
        wix_ext_out.append(ext_subst)
    return wix_ext_out


def create_version_wxi(rev):
    """
    create_version_wxi(rev):
    """
    version_cfg = get_wix_config_json().get("version", None)
    if version_cfg:
        version_cmd_line = [ 'python', os.path.join(REPOSITORY_ROOT, 'packaging/Win/bin/createVersionWxi.py'),
                            os.path.join(REPOSITORY_ROOT, version_cfg.get('version_info_file', '')),
                            rev
                            ]

        version_wxi = subprocess.getoutput(version_cmd_line)
        verbose(version_wxi)
        version_wxi_file = open('ProductVersion.wxi', 'w')
        version_wxi_file.write(version_wxi)
        version_wxi_file.close()


def heat(wix_cfg):
    """
    Harvest Tool (Heat): Generates WiX authoring from various input formats.
    Every time heat is run it regenerates the output file and any changes are lost.
    http://wixtoolset.org/documentation/manual/v3/overview/heat.html
    """
    arch = wix_cfg.get('arch', None)
    verbose("heat %s" % arch)
    heat_exe = os.path.join(WIXPATH, 'heat.exe')

    heat_cfg = get_wix_config_json().get("heat", None)
    if heat_cfg:
        for entry in heat_cfg:
            verbose("heat for %s" % entry)
            heat_cmd_line = [ heat_exe, 'dir', entry,            # Harvest a directory.
                        '-gg',                            # Generate guids now. All components are given a guid when heat is run.
                        '-scom',                          # Suppress COM elements.
                        '-sfrag',                         # Suppress generation of fragments for directories and components.
                        '-template',
                        'fragment',
                        '-sreg'                           # Suppress registry harvesting.
                        ] + heat_cfg.get(entry, [])

            verbose(heat_cmd_line)

            subprocess.check_call(heat_cmd_line)

    else:
        # generic call
        heat_cmd_line = [ heat_exe, 'dir', arch,            # Harvest a directory.
                        '-dir', 'APPLICATIONINSTALLDIR',  #
                        '-cg', 'ExtFiles',                # Component group name
                        '-dr', 'APPLICATIONINSTALLDIR',   # Directory reference to root directories
                        '-var', 'var.SDir',               # Substitute File/@Source="SourceDir" with a preprocessor or a wix variable
                        '-out', 'dir.wxs',                # Specify output file (default: write to current directory).
                        '-gg',                            # Generate guids now. All components are given a guid when heat is run.
                        '-scom',                          # Suppress COM elements.
                        '-sfrag',                         # Suppress generation of fragments for directories and components.
                        '-srd',                           # Suppress harvesting the root directory as an element.
                        '-sreg'                           # Suppress registry harvesting.
                        ]

        verbose(heat_cmd_line)
        
        subprocess.check_call(heat_cmd_line)        


def candle(wix_cfg):
    """
    Compiler (candle): The Windows Installer XML compiler is exposed by candle.exe.
    http://wixtoolset.org/documentation/manual/v3/overview/candle.html
    """
    arch = wix_cfg.get('arch', None)
    verbose("candle %s" % arch)
    candle_exe = os.path.join(WIXPATH, 'candle.exe')

    wix_ext = []
    for ext in wix_cfg.get('wix_ext', []):
        wix_ext.append('-ext')
        wix_ext.append(ext)

    wxs_files = glob.glob('*.wxs')

    # scan for additional extensions:
    for wxs in wxs_files:
        if "dir.wxs" != wxs:
            wix_ext = wix_ext + update_wix_extensions(wxs, 'candle')
    
    wix_ext = resolve_extension_path(wix_ext, wix_cfg)

    candle_cfg = get_wix_config_json().get("candle", None)
    if candle_cfg:
        candle_cmd_line = [ candle_exe, '-arch', arch,        # set architecture defaults for package,
                '-dSDir=%s' % arch,  #-d<name>[=<value>]  define a parameter for the preprocessor
            ] + candle_cfg + wix_ext + wxs_files
    else:
        candle_cmd_line = [ candle_exe, '-arch', arch,        # set architecture defaults for package,
                '-dSDir=%s' % arch,  #-d<name>[=<value>]  define a parameter for the preprocessor
            ] + wix_ext + wxs_files

    verbose(candle_cmd_line)

    subprocess.check_call(candle_cmd_line)


def light(wix_cfg):
    """
    Linker (light): The Windows Installer XML linker is exposed by light.exe.
    http://wixtoolset.org/documentation/manual/v3/overview/light.html
    """
    verbose("light")
    light_exe = os.path.join(WIXPATH, 'light.exe')

    wix_ext = []
    for ext in wix_cfg.get('wix_ext', []):
        wix_ext.append('-ext')
        wix_ext.append(ext)

    wxs_files = glob.glob('*.wxs')
    # scan for additional extensions:
    for wxs in wxs_files:
        if "dir.wxs" != wxs:
            wix_ext = wix_ext + update_wix_extensions(wxs, 'light')

    wix_ext = resolve_extension_path(wix_ext, wix_cfg)

    wixobj_files = glob.glob('*.wixobj')

    installer_file = wix_cfg.get('msi_file', None)
    assert installer_file != None, "No installer file given"

    light_cfg = get_wix_config_json().get("light", None)
    if light_cfg:
        light_cmd_line = [ light_exe ] + wix_ext + [
                '-sice:ICE38',    # Suppress running internal consistency evaluators (ICEs) with specific IDs.
                '-sval',          # Suppress MSI/MSM validation.
                '-sw1076',        # Suppress warnings with specific message IDs.
                '-out', installer_file
            ] + light_cfg + wixobj_files
    else:
        light_cmd_line = [ light_exe ] + wix_ext + [
                      '-sice:ICE38',    # Suppress running internal consistency evaluators (ICEs) with specific IDs.
                      '-sval',          # Suppress MSI/MSM validation.
                      '-sw1076',        # Suppress warnings with specific message IDs.
                      '-out', installer_file
                    ] + wixobj_files

    verbose(light_cmd_line)

    subprocess.check_call(light_cmd_line)      

def clean():
    """
    clean
    """
    verbose("Cleaning %s" % os.getcwd())
    obj_files = glob.glob('*.wixobj')
    for f in obj_files:
        os.unlink(f)

    pdb_files = glob.glob('*.wixpdb')
    for f in pdb_files:
        os.unlink(f)

    gen_wxs_files = glob.glob('dir.wxs')
    for f in gen_wxs_files:
        os.unlink(f)


def dwmsi(argv):
    """
    function interface for dwmsi. to be used if imported (instead of main)
    """
    parser = argparse.ArgumentParser(
    description='%s is a script file for signing installer, driver and executables' % sys.argv[0])

    parser.add_argument('installer_file',
                        metavar="file",
                        nargs="?",
                        default=[],
                        help='Installer file name')
    parser.add_argument('-a', '--arch', dest='arch',
                        action='store',
                        default='x64',
                        help='Set the processor architecture')
    parser.add_argument('--rev', dest='rev',
                        action='store',
                        default='1234.5',
                        help='SVN/hg revision for msi bundle build')
    parser.add_argument('--runtime_version', dest='runtime_version',
                        action='store',
                        default='vs2013',
                        help='Used Visual Studio Runtime')
    parser.add_argument('--bundle', dest='bundle',
                        action='store_true',
                        default=False,
                        help='Uses special WiX bundle signing')
    parser.add_argument('--clean', dest='clean',
                        action='store_true',
                        default=False,
                        help='Manually clean temporaries')
    parser.add_argument('--workspace', dest='workspace',
                        action='store',
                        default=None,
                        help='Set the workspace directory')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        default=False,
                        help='be more verbose')

    args = parser.parse_args(argv)

    global VERBOSE
    VERBOSE = args.verbose

    global REPOSITORY_ROOT
    if args.workspace:
        REPOSITORY_ROOT = args.workspace

    global WIXTOOLSET_EXTENSIONS

    if 'WIX' not in os.environ.keys():
        die("WIX installation not found")
    global WIXPATH
    WIXPATH = os.path.join(os.environ['WIX'], 'bin')


    wix_cfg = {
        "wix_ext" : [ '%WIX_PATH%/WixUIExtension.dll' ],
        "msi_file" : args.installer_file,
        "arch" : args.arch
    }

    if args.clean:
        clean()
        return True

    try:
        if not copy_runtime_msm(args.runtime_version, args.arch):
            die("Visual Studio Runtime msm not found")

        # gather commonly used wxi (include) files
        copy_tree(os.path.join(REPOSITORY_ROOT, 'packaging/Win/WiX'), '.')

        create_version_wxi(args.rev)

        # no heat harvester for bundles
        if not args.bundle:
            heat(wix_cfg)

        candle(wix_cfg)
        
        light(wix_cfg)

        clean()

    except RuntimeError as e:
        print("%s" % (e))
        return False

    return True

# main
if __name__ == "__main__":
    ret = dwmsi(sys.argv[1:])
    # cmdlne expexts 0 (== False) for success
    sys.exit(not ret)

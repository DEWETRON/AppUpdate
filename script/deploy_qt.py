#!/usr/bin/env python

#
# deploy_qt.py Copyright (c) Dewetron 2013
#

import argparse
import fnmatch
import os
import subprocess
import sys
import re
import shutil

ARCH_X86      = 'x86'
ARCH_X64      = 'x64'

#----------------------------------------------------------------------
def IsModuleUsed(modules, used_modules):
  for used in used_modules:
    if used in modules:
      return 1
  return 0

def FindFiles(qt_build_directory, source_dir, base_path, patterns, recursive):
    ret = []
    path = os.path.join(qt_build_directory, source_dir, base_path)
    all_files = os.listdir(path)
    for filename in all_files:
        filepath = os.path.join(path, filename)
        relpath = os.path.join(source_dir, base_path, filename)
        fakepath = os.path.join(base_path, filename)
        if os.path.isdir(filepath):
            if recursive:
                ret = ret + FindFiles(qt_build_directory, source_dir, fakepath, patterns, recursive)
        else:
            matched = False
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    matched = True
            if matched:
                ret.append([relpath, fakepath])
    return ret
  
#----------------------------------------------------------------------
class DLLEntry:
    def __init__(self, modules, source_dir, base_name, platforms, archs, has_dbg_pdb, has_rel_pdb, has_dbg_build, dbg_build_name):
        self.modules = modules
        self.source_dir = source_dir
        self.base_name = base_name
        self.platforms = platforms
        self.archs = archs
        self.has_dbg_pdb = has_dbg_pdb
        self.has_rel_pdb = has_rel_pdb
        self.has_dbg_build = has_dbg_build
        self.dbg_build_name = dbg_build_name
#----------------------------------------------------------------------
class FileEntry:
    def __init__(self, modules, source_dir, base_name, patterns=[], recursive=1):
        self.modules = modules
        self.source_dir = source_dir
        self.base_name = base_name
        self.patterns = patterns
        self.recursive = recursive
#----------------------------------------------------------------------
def CreateDLLEntry(modules, source_dir, base_name, platforms=[], archs=[], has_dbg_pdb=1, has_rel_pdb=0, has_dbg_build=1, dbg_build_name=""):
#    dll = {
#            'modules': modules,
#            'source_dir': source_dir,
#            'base_name': base_name,
#            'platforms': platforms,
#            'archs': archs,
#            'has_dbg_pdb': has_dbg_pdb,
#            'has_rel_pdb': has_rel_pdb,
#            'has_dbg_build': has_dbg_build,
#            'dbg_build_name': dbg_build_name
#         }
    dll = DLLEntry(modules, source_dir, base_name, platforms, archs, has_dbg_pdb, has_rel_pdb, has_dbg_build, dbg_build_name)
    return dll

#----------------------------------------------------------------------
class Qt511os(object):
  def __init__(self):
    self.platform = "windows"
    self.modules = ['accessible', 'angle', 'multimedia', 'network', 'print', 'quick1', 'quick2', 'script', 'test', 'widgets', 'xml', 'serialport', 'positioning', 'location']
    self.default_modules = ['widgets', 'multimedia', 'network', 'print', 'xml', 'quick1', 'quick2', 'test', 'accessible']
    comp_none = ['none']
    comp_accessible = ['accessible']
    comp_angle = ['angle']
    comp_base = []
    comp_multimedia = ['multimedia']
    comp_network = ['network']
    comp_print = ['print']
    comp_quick = ['quick1','quick2']
    comp_script = ['script']
    comp_test = ['test']
    comp_widgets = ['widgets']
    comp_xml = ['xml']
    comp_serialport = ['serialport']

# entries should have module, source_dir, base_name, plaforms, archs, has_rel_pdb, has_dbg_pdb, has_std_dbg_name, debug_name [use this instead of ...d?]
# call generator function that creates a DLLInfo object (with sensible defaults for everything except module, source_dir & base_name)
    self.dlls = [
            #               modules     source_dir  base_name
            CreateDLLEntry( comp_xml,     'lib', 'Qt5Xml' ),
            CreateDLLEntry( comp_xml,     'lib', 'Qt5XmlPatterns' ),
            CreateDLLEntry( comp_none,    'lib', 'Qt5CLucene' ),
            CreateDLLEntry( comp_base,    'lib', 'Qt5Concurrent' ),
            CreateDLLEntry( comp_base,    'lib', 'Qt5Core' ),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5Declarative' ),
            CreateDLLEntry( comp_widgets, 'lib', 'Qt5Gui' ),
            CreateDLLEntry( comp_none,    'lib', 'Qt5Help' ),
            CreateDLLEntry( comp_multimedia,    'lib', 'Qt5Multimedia' ),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5MultimediaQuick_p' ),
            CreateDLLEntry( comp_multimedia, 'lib', 'Qt5MultimediaWidgets' ),
            CreateDLLEntry( comp_network, 'lib', 'Qt5Network' ),
            CreateDLLEntry( comp_base,    'lib', 'Qt5OpenGL', platforms=['linux'] ),
            CreateDLLEntry( comp_print,   'lib', 'Qt5PrintSupport' ),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5Qml' ),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5Quick' ),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5QuickParticles' ),
            CreateDLLEntry( comp_test,    'lib', 'Qt5QuickTest' ),
            CreateDLLEntry( comp_script,  'lib', 'Qt5Script' ),
            CreateDLLEntry( comp_script,  'lib', 'Qt5ScriptTools' ),
            CreateDLLEntry( comp_none,    'lib', 'Qt5Sensors' ),
            CreateDLLEntry( comp_none,    'lib', 'Qt5SerialPort' ),
            CreateDLLEntry( comp_base,    'lib', 'Qt5Sql', platforms=['linux']),
            CreateDLLEntry( comp_base,    'lib', 'Qt5Svg' ),
            CreateDLLEntry( comp_test,    'lib', 'Qt5Test' ),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5V8' ),
            CreateDLLEntry( comp_widgets, 'lib', 'Qt5Widgets' ),
            CreateDLLEntry( comp_angle,   'lib', 'libEGL', ['windows'] ),
            CreateDLLEntry( comp_angle,   'lib', 'libGLESv2', ['windows'] ),
            CreateDLLEntry( comp_angle,   '3rdparty/x86', 'D3DCompiler_43', platforms=['windows'], archs=['x86'], has_dbg_build=0 ),
            CreateDLLEntry( comp_angle,   '3rdparty/x64', 'D3DCompiler_43', platforms=['windows'], archs=['x64'], has_dbg_build=0 ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qtiff' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qwbmp' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qgif' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qico' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qjpeg' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qmng' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qsvg' ),
            CreateDLLEntry( comp_base,    'plugins', 'imageformats/qtga' ),
            CreateDLLEntry( comp_quick,   'plugins', 'qmltooling/qmldbg_qtquick2' ),
            CreateDLLEntry( comp_quick,   'plugins', 'qmltooling/qmldbg_tcp' ),
            CreateDLLEntry( comp_base,    'plugins', 'iconengines/qsvgicon' ),
            CreateDLLEntry( comp_base,    'plugins', 'platforms/qminimal' , platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_base,    'plugins', 'platforms/qoffscreen', platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_base,    'plugins', 'platforms/qxcb', platforms=['linux'] ),
            CreateDLLEntry( comp_base,    'plugins', 'platforms/qwindows', platforms=['windows'] ),
            CreateDLLEntry( comp_print,   'plugins', 'printsupport/windowsprintersupport' , platforms=['windows'] ),
            CreateDLLEntry( comp_print,   'plugins', 'printsupport/cocoaprintersupport' , platforms=['osx'] ),
            CreateDLLEntry( comp_quick,   'qml', 'QtQuick.2/qtquick2plugin', platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_quick,   'qml', 'Qt/labs/folderlistmodel/qmlfolderlistmodelplugin', platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_quick,   'qml', 'Qt/labs/settings/qmlsettingsplugin', platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_quick,   'qml', 'QtGraphicalEffects/private/qtgraphicaleffectsprivate', platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_quick,   'qml', 'QtGraphicalEffects/qtgraphicaleffectsplugin', platforms=['linux','windows','osx'] ),
            CreateDLLEntry( comp_accessible,'plugins', 'accessible/qtaccessiblequick' ),
            CreateDLLEntry( comp_accessible,'plugins', 'accessible/qtaccessiblewidgets' ),
            CreateDLLEntry( comp_serialport,'lib', 'QT5SerialPort' ),
            CreateDLLEntry( comp_base,    'lib', 'Qt5DBus', platforms=['linux'] ),
            CreateDLLEntry( comp_base,    'lib', 'Qt5XcbQpa', platforms=['linux'] ),
            CreateDLLEntry( comp_base,    'plugins', 'xcbglintegrations/qxcb-glx-integration', platforms=['linux'] ),
            CreateDLLEntry( comp_base,    'plugins', 'xcbglintegrations/qxcb-egl-integration', platforms=['linux'] ),
            # currently not used but needed to completely fullfill QtQuick dependencies (at least for linux):
            CreateDLLEntry( comp_quick,   'lib', 'Qt53DRender', platforms=['linux']),
            CreateDLLEntry( comp_quick,   'lib', 'Qt53DCore', platforms=['linux']),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5QuickControls2'),
            CreateDLLEntry( comp_quick,   'lib', 'Qt53DInput', platforms=['linux']),
            CreateDLLEntry( comp_quick,   'lib', 'Qt53DLogic', platforms=['linux']),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5QuickTemplates2'),
            CreateDLLEntry( comp_quick,   'lib', 'Qt5Gamepad', platforms=['linux']),
            CreateDLLEntry( comp_quick,   'lib', 'Qt53DQuickScene2D', platforms=['linux']),
        ]

# entries should have module, source_dir, base_name
    self.files = [
            FileEntry( comp_quick,    'qml', 'QtQuick.2/qmldir'),
            FileEntry( comp_quick,    'qml', 'Qt/labs/folderlistmodel/qmldir'),
            FileEntry( comp_quick,    'qml', 'Qt/labs/settings/qmldir'),
            FileEntry( comp_quick,    'qml', 'QtGraphicalEffects', ['qmldir', '*.qml'], True),
        ]
        
  def getId(self):
    return '5.1.1'

  def getName(self):
    return 'Qt 5.1.1 Open Source'

  def getBuildName(self, platform, arch, special_build):
    name = self.getId() + "_"


    if platform=="windows":
      name = name + "win"
    elif platform=="linux":
      name = name + "lin"
    elif platform=="osx":
      name = name + "osx"
    else:
        return ""

    self.platform = platform

    if arch=='x64':
        name = name + "64"
    elif arch=='x86':
        name = name + "32"
    else:
        return ""

    if special_build:
        name = name + "_" + special_build

    return name

  def getModules(self):
    return self.modules

  def getDefaultModules(self):
    return self.default_modules

  def getFiles(self, platform, arch, debug_build, modules, qt_build_directory):
    files = []
    files = self.getDLLs(platform, arch, debug_build, 0, modules)

    for more_files in self.files:
        if more_files.modules==[] or IsModuleUsed(more_files.modules, modules):
            if more_files.patterns:
                files = files + FindFiles(qt_build_directory, more_files.source_dir, more_files.base_name, more_files.patterns, more_files.recursive)
            else:
                files.append([os.path.join(more_files.source_dir, more_files.base_name), more_files.base_name])

    #todo: only copy the necessary dlls from the following directories
    if IsModuleUsed(['quick1','quick2'], modules):
        files.append(['qml/QtQuick', 'QtQuick'])
    if IsModuleUsed(['test'], modules):
        files.append(['qml/QtTest', 'QtTest'])
    return files

  def isDLLRequired(self, dll, platform, arch):
    if dll.platforms==[] or platform in dll.platforms:
        pass
    else:
        return 0
    if dll.archs==[] or arch in dll.archs:
        pass
    else:
        return 0
    return 1

  def getDLLs(self, platform, arch, debug_build, pdb, modules):
    src_dlls = self.dlls

    dlls = []
    for dll in src_dlls:
        if dll.modules==[] or IsModuleUsed(dll.modules, modules):
            if self.isDLLRequired(dll, platform, arch):
                if debug_build and dll.has_dbg_build:
                    if not dll.dbg_build_name:
                        dll_path = dll.base_name+"d"
                    else:
                        dll_path = dll.dbg_build_name
                else:
                    dll_path = dll.base_name

                if platform == "windows":
                    dlls.append([dll.source_dir+"/"+dll_path+".dll", dll_path+".dll"])
                    if pdb:
                        dlls.append([dll.source_dir+"/"+dll_path+".pdb", dll_path+".pdb"])
                else:
                    dll_dir  = os.path.dirname(dll_path)
                    if len(dll_dir) > 0:
                        dll_path = "%s/lib%s.so" % (dll_dir, os.path.basename(dll_path))
                    else:
                        dll_path = "lib%s.so" % (os.path.basename(dll_path))
                    dlls.append([dll.source_dir+"/"+dll_path, dll_path])
    return dlls

#----------------------------------------------------------------------
class Qt520os(Qt511os):
  def __init__(self):
    Qt511os.__init__(self)
    for dll in self.dlls:
        if dll.base_name.find('Qt5V8')!=-1:
            self.dlls.remove(dll)

    comp_location = ['location']
    comp_position = ['positioning']
    self.dlls.append(CreateDLLEntry( comp_location, 'lib', 'Qt5Location' ))
    self.dlls.append(CreateDLLEntry( comp_location, 'qml', 'QtLocation/declarative_location', platforms=['linux','windows','osx'] ))
    self.dlls.append(CreateDLLEntry( comp_location, 'plugins', 'geoservices/qtgeoservices_osm', platforms=['linux','windows','osx'] ))
    self.dlls.append(CreateDLLEntry( comp_location, 'plugins', 'geoservices/qtgeoservices_itemsoverlay', platforms=['linux','windows','osx'] ))
    self.dlls.append(CreateDLLEntry( comp_position, 'lib', 'Qt5Positioning' ))
    self.dlls.append(CreateDLLEntry( comp_position, 'qml', 'QtPositioning/declarative_positioning', platforms=['linux','windows','osx'] ))

    self.files.append(FileEntry( comp_location, 'qml', 'QtLocation/qmldir'))
    self.files.append(FileEntry( comp_position, 'qml', 'QtPositioning/qmldir'))


  def getId(self):
    return '5.2.0'

  def getName(self):
    return 'Qt 5.2.0 Open Source'

#----------------------------------------------------------------------
class Qt530os(Qt520os):
  def __init__(self):
    Qt520os.__init__(self)

  def getId(self):
    return '5.3.0'

  def getName(self):
    return 'Qt 5.3.0 Open Source'

#----------------------------------------------------------------------
class Qt531os(Qt530os):
  def __init__(self):
    Qt530os.__init__(self)
    # Windows: dll are no longer in lib, but in bin
    if "win32" in sys.platform:
      self.changeDLLPath("lib", "bin")

  def changeDLLPath(self, from_path, to_path):
    for dll_entry in self.dlls:
      if dll_entry.source_dir == from_path:
        dll_entry.source_dir = to_path

  def getId(self):
    return '5.3.1'

  def getName(self):
    return 'Qt 5.3.1 Open Source'

#----------------------------------------------------------------------
class Qt560os(Qt531os):
  def __init__(self):
    Qt531os.__init__(self)
    
    filter_out = ['Qt5Declarative', 'accessible/qtaccessiblewidgets', 'accessible/qtaccessiblequick', 'imageformats/qmng', 'qmltooling/qmldbg_qtquick2']
    filtered_dlls = set()
    
    for dll in self.dlls:
        for f in filter_out:
            if dll.base_name.find(f)!=-1:
                filtered_dlls.add(dll)
    self.dlls = list(set(self.dlls)-filtered_dlls)
                
  def getId(self):
    return '5.6.0'

  def getName(self):
    return 'Qt 5.6.0 Open Source'

#----------------------------------------------------------------------
class Qt590os(Qt560os):
  def __init__(self):
    Qt560os.__init__(self)

  def getId(self):
    return '5.9.0'

  def getName(self):
    return 'Qt 5.9.0 Open Source'

  def getBuildName(self, platform, arch, special_build):
    name = self.getId() + "_"


    if platform=="windows":
      name = name + "win"
    elif platform=="linux":
      name = name + "lin"
    elif platform=="osx":
      name = name + "osx"
    else:
        return ""

    self.platform = platform

    if arch=='x64':
        name = name + "64"
    elif arch=='x86':
        name = name + "32"
    else:
        return ""

    return name


#----------------------------------------------------------------------
class Qt591os(Qt590os):
  def __init__(self):
    Qt590os.__init__(self)

  def getId(self):
    return '5.9.1'

  def getName(self):
    return 'Qt 5.9.1 Open Source'

#----------------------------------------------------------------------
class Qt592os(Qt591os):
  def __init__(self):
    Qt591os.__init__(self)

  def getId(self):
    return '5.9.2'

  def getName(self):
    return 'Qt 5.9.2 Open Source'

#----------------------------------------------------------------------
class Qt5125os(Qt592os):
  def __init__(self):
    Qt592os.__init__(self)

    filter_out = ['Qt5MultimediaQuick_p']
    filtered_dlls = set()
    
    for dll in self.dlls:
        for f in filter_out:
            if dll.base_name.find(f)!=-1:
                filtered_dlls.add(dll)
    self.dlls = list(set(self.dlls)-filtered_dlls)

    comp_quick = ['quick1','quick2']
    comp_position = ['positioning']
    comp_base = []
    comp_angle = ['angle']
    self.dlls.append(CreateDLLEntry( comp_quick,   'bin', 'Qt5MultimediaQuick'))
    self.dlls.append(CreateDLLEntry( comp_position, 'bin', 'Qt5PositioningQuick'))
    self.dlls.append(CreateDLLEntry( comp_base,    'plugins', 'styles/qwindowsvistastyle'))

  def getId(self):
    return '5.12.5'

  def getName(self):
    return 'Qt 5.12.5 Open Source'


#----------------------------------------------------------------------
class Qt5126os(Qt592os):
  def __init__(self):
    Qt592os.__init__(self)

    filter_out = ['Qt5MultimediaQuick_p', 'D3DCompiler_43']
    filtered_dlls = set()
    
    for dll in self.dlls:
        for f in filter_out:
            if dll.base_name.find(f)!=-1:
                filtered_dlls.add(dll)
    self.dlls = list(set(self.dlls)-filtered_dlls)

    comp_quick = ['quick1','quick2']
    comp_position = ['positioning']
    comp_base = []
    comp_angle = ['angle']
    self.dlls.append(CreateDLLEntry( comp_quick,   'bin', 'Qt5MultimediaQuick'))
    self.dlls.append(CreateDLLEntry( comp_position, 'bin', 'Qt5PositioningQuick'))
    self.dlls.append(CreateDLLEntry( comp_angle,   'bin', 'd3dcompiler_47', platforms=['windows'], has_dbg_build=0 ))
    self.dlls.append(CreateDLLEntry( comp_base,    'plugins', 'styles/qwindowsvistastyle'))

  def getId(self):
    return '5.12.6'

  def getName(self):
    return 'Qt 5.12.6 Open Source'


#----------------------------------------------------------------------
class Qt5140os(Qt5126os):
  def __init__(self):
    Qt5126os.__init__(self)

    filter_out = []
    filtered_dlls = set()
    
    for dll in self.dlls:
        for f in filter_out:
            if dll.base_name.find(f)!=-1:
                filtered_dlls.add(dll)
    self.dlls = list(set(self.dlls)-filtered_dlls)

    comp_quick = ['quick1','quick2']
    self.dlls.append(CreateDLLEntry( comp_quick,   'bin', 'Qt5QmlModels'))
    self.dlls.append(CreateDLLEntry( comp_quick,   'bin', 'Qt5QmlWorkerScript'))
    self.dlls.append(CreateDLLEntry( comp_quick,   'qml', 'QtQml/qmlplugin', platforms=['linux','windows','osx'] ))


    self.files.append(FileEntry( comp_quick,    'qml', 'QtQml/qmldir'))

  def getId(self):
    return '5.14.0'

  def getName(self):
    return 'Qt 5.14.0 Open Source'


QT_VERSIONS   = [Qt5126os(), Qt5125os(), Qt560os(), Qt590os(), Qt591os(), Qt592os(), Qt531os(), Qt530os(), Qt520os(), Qt511os(), Qt5140os()]

def copytree(src, dst):
  """
  custom version of shutil.copytree:
   - overwrites existing files
   - copies files without extension
  """
  dir_infos = os.walk(src)

  for dir_info in dir_infos:
    src_path = dir_info[0]
    dst_path = os.path.join(dst, os.path.relpath(src_path, src))

    if not os.path.exists(dst_path):
      os.makedirs(dst_path)

    for filename in dir_info[2]:

      # do not copy so.debug libraries
      if filename.endswith(".so.debug"):
        continue
      
      
      dst_name = os.path.join(dst_path, filename)
      src_name = os.path.join(src_path, filename)
      
      if os.path.exists(dst_name):
        os.remove(dst_name)

      shutil.copy(src_name, dst_name)
      shutil.copystat(src_name, dst_name)
      if args.verbose:
        print("  copy %s => %s" % (src_name, dst_name))
            
def deploy(in_file, out_file, dry_run):
  """
  Windows: copy files and directories
  Linux: copy files and directory and find so symlinks
  """
  
  if dry_run:
    return

  if os.path.isdir(in_file):
    print("deploy dir %s => %s" % (in_file, out_file))
    copytree(in_file, out_file)
  else:
      
    print("deploy file %s => %s" % (in_file, out_file))
    if os.path.islink(in_file):
      source_file = os.path.join(os.path.dirname(in_file), os.readlink(in_file))
      dest_file   = os.path.join(os.path.dirname(out_file), os.readlink(in_file))
      if os.path.exists(dest_file):
        os.remove(dest_file)
      shutil.copyfile(source_file, dest_file)
      shutil.copystat(source_file, dest_file)
    else:
      if os.path.exists(out_file):
        os.remove(out_file)

      shutil.copyfile(in_file, out_file)
      shutil.copystat(in_file, out_file)
  
#----------------------------------------------------------------------
def main(argv):
    local_directory = os.path.dirname(__file__)
    qt_builds_directory = os.path.abspath(os.path.join(local_directory, '../../opt/qt'))
    # Fallback for old 3rdparty library structure
    if not os.path.exists(qt_builds_directory):
        qt_builds_directory = os.path.abspath(os.path.join(local_directory, '../../3rdparty/qt'))

    parser = argparse.ArgumentParser(description='deploy_qt.py copies as necessary runtime files for qt applications')
    parser.add_argument('--arch', dest='architecture',
                        action='store',
                        choices=[ARCH_X86,ARCH_X64],
                        default=ARCH_X64,
                        help='select the architecture of the build (x86 = 32bit, x64 = 64bit (default))')

#    parser.add_argument('--platform', dest='platform',
#                        action='store',
#                        choices=['windows','linux'],
#                        default='windows',
#                        help='select the platform. Host platform is the default')

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
                        default=qt_builds_directory,
                        help='specify the directory where the qt install directories are located')

    parser.add_argument('--special-build', '--special_build', dest='special_build',
                        action='store',
                        default=None,
                        help='select a special build variant (e.g. "angle")')

    parser.add_argument('--dry', dest='dry_run',
                        action='store_true',
                        default=False,
                        help='Only simulate the deployment operation')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        default=False,
                        help='Only simulate the deployment operation')

    qt_version_keys = []
    for qt in QT_VERSIONS:
      qt_version_keys.append(qt.getId())

    parser.add_argument('--qt-version', '--qt_version', dest='qt_version',
                        action='store',
                        choices=qt_version_keys,
                        default=qt_version_keys[0],
                        help='select the required Qt verison. '+str(QT_VERSIONS[0].getId())+' ('+str(QT_VERSIONS[0].getName())+') is the default')

    parser.add_argument('--qt-module', '--qt_module', dest='module',
                        action='append',
                        choices=['accessible', 'angle', 'multimedia', 'network', 'print', 'quick1', 'quick2', 'script', 'test', 'widgets', 'xml', 'serialport', 'positioning', 'location'], #todo: get from qt
                        default=[],
                        help='default: deploy all supported modules')

    parser.add_argument('--oxygen', dest='module',
                        action='store_const',
                        const=['multimedia', 'network', 'print', 'quick2', 'widgets', 'xml', 'positioning', 'location'],
                        help='adds all modules required by oxygen to the "deploy" list (use before other --qt-module args!)')

    global args
    args = parser.parse_args()

    print(args)

    if not args.destination:
        print("Error: please specify --destination folder")
        return 1

    selected_qt = 0
    selected_modules = args.module

    for qt in QT_VERSIONS:
      if qt.getId()==args.qt_version:
        selected_qt = qt

    #if no modules are specified => use all
    if not selected_modules:
        selected_modules = selected_qt.getDefaultModules()
    else:
        #convenience: automatically select angle module if such a build is used
        if args.special_build == 'angle' \
          and 'angle' not in selected_modules \
          and 'angle' in selected_qt.getModules() \
          and 'quick2' in selected_modules:
            selected_modules.append('angle')
        #todo: check if all specified modules are valid
        pass

    debug_build = 0
    if args.build_type=="Debug":
      debug_build = 1

    platform = ""
    if "win32" in sys.platform:
      platform = "windows"
    elif "linux" in sys.platform:
      platform = "linux"
    elif "darwin" in sys.platform:
      platform = "osx"
    else:
      raise RuntimeException("unsupported platform %s" % (sys.platform))

    qt_build_name = selected_qt.getBuildName(platform, args.architecture, args.special_build)

    if os.path.exists(args.qt_directory):
      qt_build_directory = os.path.normpath(os.path.join(args.qt_directory, qt_build_name))
    else:
      qt_build_directory = os.path.normpath(os.path.join(qt_builds_directory, qt_build_name))
    destination_directory = os.path.abspath(args.destination)

    if not os.path.exists(qt_build_directory):
      print("Error: qt directory "+qt_build_directory+" does not exist")
      return 2

    if not os.path.exists(destination_directory):
      try:
        os.makedirs(destination_directory)
      except OSError as e:
        pass

    print("Selected Qt Version: "+str(selected_qt.getName()))
    print("Selected Modules: "+str(selected_modules))

    # get list of files to deploy
    files = selected_qt.getFiles(platform, args.architecture, debug_build, selected_modules, qt_build_directory)

    # copy files or folders
    for file in files:
        in_file = os.path.normpath(os.path.join(qt_build_directory, file[0]))
        out_file = os.path.normpath(os.path.join(destination_directory, file[1]))
        out_dir = os.path.dirname(out_file)


        if not os.path.exists(out_dir):
          try:
            os.makedirs(out_dir)
          except OSError as e:
            pass

        deploy(in_file, out_file, args.dry_run)
          
    # post deployment steps:
    if "linux" in sys.platform:
      if not args.dry_run:
        os.system("ldconfig -n %s" % destination_directory)

    
    return 0

#----------------------------------------------------------------------
# main
if __name__ == "__main__":
    ret = main(sys.argv)
    sys.exit(ret)

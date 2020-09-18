#!/usr/bin/env python
import argparse
import os
import sys

#python %WORKSPACE%/packaging/Win/bin/versionize_filename.py -f DEWETRON-TRION-Applications-%ARCH%.exe --version_header %WORKSPACE%/api/trion_version/MajorVersion.h --revision %VER% 

parser = argparse.ArgumentParser(description='add version suffix to given file')
parser.add_argument('-f', '--file', dest='file',
                    action='store',
                    default=None,
                    help='Filename to change')
parser.add_argument('--version_header', dest='version_header',
                    action='store',
                    default=None,
                    help='Header containing MAJOR,MINOR')
parser.add_argument('-r', '--revision', dest='revision',
                    action='store',
                    default='0',
                    help='build revision')


args = parser.parse_args()

f = open(args.version_header)

major = 1
minor = 0
micro = 0
revision = args.revision


for l in f:   
    if "VERSION_MAJOR" in l:
        major=l.split()[2]
    if "VERSION_MINOR" in l:
        minor=l.split()[2]
    if "VERSION_MICRO" in l:
        micro=l.split()[2]

base_name = os.path.splitext(args.file)[0]
new_file_name = "%s-%s-%s-%s-%s" % (base_name, major, minor, micro, revision) + os.path.splitext(args.file)[1]
print(new_file_name)

os.rename(args.file, new_file_name)
os.remove(args.file)

sys.exit(0)
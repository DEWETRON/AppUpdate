# ProductVersion.wxi

import sys

if len(sys.argv) == 1:
    sys.exit(1)

f = open(sys.argv[1])

major = 1
minor = 0
micro = 0
revision = 0

if len(sys.argv) > 2:
    revision = sys.argv[2]

for l in f:   
    if "VERSION_MAJOR" in l:
        major=l.split()[2]
    if "VERSION_MINOR" in l:
        minor=l.split()[2]
    if "VERSION_MICRO" in l:
        micro=l.split()[2]


print('<Include><?define PRODUCT_VERSION="%s.%s.%s.%s"?></Include>' % (major, minor, micro, revision))

sys.exit(0)
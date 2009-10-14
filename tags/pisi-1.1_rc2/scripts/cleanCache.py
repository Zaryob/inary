#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import string
import pisi.util as util
from pisi.version import Version

def findUnneededFiles():
    listdir = map(lambda x: os.path.basename(x), glob.glob("/var/cache/pisi/packages/*.pisi"))
    listdir.sort()

    dict = {}
    for f in listdir:
        name, ver = util.parse_package_name(f)
        version = ver.split(".pisi")[0]
        if dict.has_key(name):
            if Version(dict[name]) < Version(version):
                dict[name] = version
        else:
            dict[name] = version

    for f in dict:
        listdir.remove("%s-%s.pisi" % (f, dict[f]))

    return listdir

def usage(msg):
    print """
Error: %s

Usage:
    cleanCache --dry-run    (Shows unneeded files)
    cleanCache --clean      (Removes unneeded files)
    """ % msg

    sys.exit(1)

if __name__ == "__main__":
    try:
        sys.argv[1]
    except IndexError:
        usage("Unsufficient arguments...")

    if sys.argv[1] == "--dry-run":
        for i in findUnneededFiles():
            if os.path.exists("/var/cache/pisi/packages/%s" % i):
                print i
    elif sys.argv[1] == "--clean":
        for i in findUnneededFiles():
            if os.path.exists("/var/cache/pisi/packages/%s" % i):
                try:
                    os.remove("/var/cache/pisi/packages/%s" % i)
                except OSError:
                    usage("Permission denied...")
    else:
        usage("No command given...")

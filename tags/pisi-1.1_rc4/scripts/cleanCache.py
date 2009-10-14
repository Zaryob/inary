#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import string
import pisi.util as util
from pisi.version import Version

def findUnneededFiles(listdir):
    dict = {}
    for f in listdir:
        try:
            name, version = util.parse_package_name(f)
            if dict.has_key(name):
                if Version(dict[name]) < Version(version):
                    dict[name] = version
            else:
                if version:
                    dict[name] = version

        except:
            pass

    for f in dict:
        listdir.remove("%s-%s" % (f, dict[f]))

    return listdir

def doit(root, listdir, clean, suffix = ""):
    print "Working in %s" % root
    for f in listdir:
        target = os.path.join(root, "%s%s" % (f, suffix))
        if os.path.exists(target):
            print "%s%s" % (f, suffix)
            if clean == True:
                try:
                    if os.path.isdir(target):
                        os.removedirs(target)
                    else:
                        os.remove(target)
                except OSError:
                    usage("Permission denied...")


def cleanPisis(clean, root = '/var/cache/pisi/packages'):
    # pisi packages
    list = map(lambda x: os.path.basename(x).split(".pisi")[0], glob.glob("%s/*.pisi" % root))
    list.sort()
    l = findUnneededFiles(list)
    doit(root, l, clean, ".pisi")

def cleanBuilds(clean, root = '/var/tmp/pisi'):
    # Build remnant
    list = []
    for f in os.listdir(root):
        if os.path.isdir(os.path.join(root, f)):
             list.append(f)

    l = findUnneededFiles(list)
    doit(root, l, clean)

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

    if "--dry-run" in sys.argv:
        print "Running in dry-run mode"
        clean = False
    elif "--clean" in sys.argv:
        print "Say bye bye to your files"
        clean = True
    else:
        usage("No command given...")
        sys.exit(0)

    if "builds" in sys.argv:
        cleanBuilds(clean)

    else:
        cleanPisis(clean)


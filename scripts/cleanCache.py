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
        if os.path.exists("%s/%s%s" % (root, f, suffix)):
            print "%s%s" % (f, suffix)
            if clean == True:
                try:
                    os.remove("%s/%s" % (root, f))
                except OSError:
                    usage("Permission denied...")


def cleanPisis(clean, root):
    # pisi packages
    root = "/var/cache/pisi/packages"
    list = map(lambda x: os.path.basename(x).split(".pisi")[0], glob.glob("%s/*.pisi" % root))
    l = findUnneededFiles(list)
    doit(root, l, clean, ".pisi")

def cleanBuilds(clean, root):
    # Build remnant
    root = "/var/tmp/pisi"
    l = []
    for f in os.listdir(root):
        if os.path.isdir(os.path.join(root, f)):
             l.append(f)
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
        root = "/var/tmp/pisi"
        cleanBuilds(clean, root)

    else:
        root = "/var/cache/pisi/packages"
        cleanPisis(clean, root)


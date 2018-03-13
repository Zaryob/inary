#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys
import glob
import string
import shutil
import inary.util as util
from inary.version import Version

def findUnneededFiles(listdir):
    dict = {}
    for f in listdir:
        try:
            name, version = util.parse_package_name(f)
            if name in dict:
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
    for f in listdir:
        target = os.path.join(root, "%s%s" % (f, suffix))
        if os.path.exists(target):
            print(("%s%s" % (f, suffix)))
            if clean == True:
                try:
                    if os.path.isdir(target):
                        shutil.rmtree(target)
                    else:
                        os.remove(target)
                except OSError as e :
                    usage("Permission denied: %s" % e)


def cleanInarys(clean, root = '/var/cache/inary/packages'):
    # inary packages
    list = [os.path.basename(x).split(".inary")[0] for x in glob.glob("%s/*.inary" % root)]
    list.sort()
    l = findUnneededFiles(list)
    doit(root, l, clean, ".inary")

def cleanBuilds(clean, root = '/var/inary'):
    # Build remnant
    list = []
    for f in os.listdir(root):
        if os.path.isdir(os.path.join(root, f)):
             list.append(f)

    l = findUnneededFiles(list)
    doit(root, l, clean)

def usage(msg):
    print(("""
Error: %s

Usage:
    cleanCache --dry-run    (Shows unneeded files)
    cleanCache --clean      (Removes unneeded files)
    """ % msg))

    sys.exit(1)

if __name__ == "__main__":
    try:
        sys.argv[1]
    except IndexError:
        usage("Unsufficient arguments...")

    if "--dry-run" in sys.argv:
        clean = False
    elif "--clean" in sys.argv:
        clean = True
    else:
        usage("No command given...")
        sys.exit(0)

    if "builds" in sys.argv:
        cleanBuilds(clean)

    else:
        cleanInarys(clean)

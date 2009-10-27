#!/usr/bin/python
#
# Copyright (C) 2005, 2006 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys

import pisi.uri
import pisi.specfile

def scanPSPEC(folder):
    packages = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            packages.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return packages

def cleanArchives(file):
    try:
        os.remove(file)
    except OSError:
        print("Permission denied...")

if __name__ == "__main__":
    try:
        packages = scanPSPEC(sys.argv[1])
    except:
        print "Usage: cleanArchives.py path2repo"
        sys.exit(1)

    if "--dry-run" in sys.argv:
        clean = False
    elif "--clean" in sys.argv:
        clean = True
    else:
        sys.exit(0)

    files = []
    for package in packages:
        spec = pisi.specfile.SpecFile()
        spec.read(os.path.join(package, "pspec.xml"))

        URI = pisi.uri.URI(spec.source.archive.uri)
        files.append(URI.filename())

    archiveFiles = os.listdir("/var/cache/pisi/archives/")
    unneededFiles = filter(lambda x:x not in files, archiveFiles)

    for i in unneededFiles:
        if not clean:
            print("/var/cache/pisi/archives/%s" % i)
        else:
            cleanArchives("/var/cache/pisi/archives/%s" % i)

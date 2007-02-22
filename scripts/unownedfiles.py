#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import os
import sys
import piksemel


def findFilesXML(path):
    filesXMLs = list()
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == "files.xml":
                filesXMLs.append(os.path.join(root, file))
    return filesXMLs

def parseFilesXML():
    files = set()
    for filesXML in findFilesXML("/var/lib/pisi/package/"):
        data = open(filesXML).read()
        data = piksemel.parseString(data)
        for filePath in data.tags("File"):
            path = filePath.getTagData("Path")
            if filePath.getTag("Hash"):
                files.add("/%s" % path)
    return files

if __name__ == "__main__":
    try:
        sys.argv[1]
    except IndexError:
        sys.exit("Unsufficient arguments...")

    fileSet = parseFilesXML()

    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            f = os.path.join(root, file)
            if not fileSet.__contains__(f):
                print f

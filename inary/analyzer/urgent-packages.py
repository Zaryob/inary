# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import ciksemel
import bz2
import sys
import os


def loadFile(_file):
    try:
        f = open(_file)
        d = [a.lstrip().rstrip("\n") for a in f]
        d = [x for x in d if not (x.startswith("#") or x == "")]
        f.close()
        return d
    except:
        return []

def getXmlData(_file):
    if os.path.exists(_file):
        return minidom.parse(_file).documentElement
    elif os.path.exists("{}.bz2".format(_file)):
        indexdata = bz2.decompress(open("{}.bz2".format(_file)).read())
        return minidom.parseString(indexdata)
    else:
        print("{} not found".format(indexfile))
        sys.exit(1)

def fillPackageDict(tag, _hasSpecFile, packageOf):
        PackagePartOf = tag.getElementsByTagName("PartOf")[0]
        PackageName = tag.getElementsByTagName("Name")[0]

        if _hasSpecFile:
            PackagePackagerName = tag.getElementsByTagName("Packager")[0].getElementsByTagName("Name")[0].firstChild.data
        else:
            PackagePackagerName = tag.getElementsByTagName("Source")[0].getElementsByTagName("Packager")[0].getElementsByTagName("Name")[0].firstChild.data

        fullpath = "{0}/{1}".format(PackagePartOf.replace(".", "/"), PackageName)

        if not PackagePackagerName in packageOf:
            packageOf[PackagePackagerName] = []
        packageOf[PackagePackagerName].append(fullpath)

def parseXmlData(_index):
    packageOf = {}
    hasSpecFile = _index.getTag("SpecFile")
    if hasSpecFile:
        for i in _index.tags("SpecFile"):
            parent = i.getTag("Source")
            fillPackageDict(parent, hasSpecFile, packageOf)
    else:
        for parent in _index.tags("Package"):
            fillPackageDict(parent, hasSpecFile, packageOf)

    return packageOf

def findRequiredPackages(packageList, packagersList):
    pkgdict = {}

    for pkg in packageList:
        for packager in packagersList:
            for sourcePackage in packagersList[packager]:
                if sourcePackage.endswith("/{}".format(pkg)):
                    if not packager in pkgdict:
                        pkgdict[packager] = []
                    pkgdict[packager].append(pkg)

    return pkgdict

def urgent_packages(index, packages):
    indexfile = "{0}/{1}".format(index, "inary-index.xml")
    packageList = loadFile(packages)

    xmldata = getXmlData(indexfile)
    packagers = parseXmlData(xmldata)

    requiredPackages = findRequiredPackages(packageList, packagers)

    tmp = list(requiredPackages.keys())
    tmp.sort()

#    for i in tmp:
#        print("-> %s" % i)
#        for k in requiredPackages[i]:
#             print("\t%s" % k)

# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
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
        return ciksemel.parse(_file)
    elif os.path.exists("%s.bz2" % _file):
        indexdata = bz2.decompress(file("%s.bz2" % _file).read())
        return ciksemel.parseString(indexdata)
    else:
        print("%s not found" % indexfile)
        sys.exit(1)

def fillPackageDict(tag, _hasSpecFile, packageOf):
        PackagePartOf = tag.getTagData("PartOf")
        PackageName = tag.getTagData("Name")

        if _hasSpecFile:
            PackagePackagerName = tag.getTag("Packager").getTagData("Name")
        else:
            PackagePackagerName = tag.getTag("Source").getTag("Packager").getTagData("Name")

        fullpath = "%s/%s" % (PackagePartOf.replace(".", "/"), PackageName)

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
                if sourcePackage.endswith("/%s" % pkg):
                    if not packager in pkgdict:
                        pkgdict[packager] = []
                    pkgdict[packager].append(pkg)

    return pkgdict

def urgent_packages(index, packages):
    indexfile = "%s/%s" % (index, "inary-index.xml")
    packageList = loadFile(packages)

    xmldata = getXmlData(indexfile)
    packagers = parseXmlData(xmldata)

    requiredPackages = findRequiredPackages(packageList, packagers)

    tmp = list(requiredPackages.keys())
    tmp.sort()

    for i in tmp:
        print("-> %s" % i)
        for k in requiredPackages[i]:
             print("\t%s" % k)


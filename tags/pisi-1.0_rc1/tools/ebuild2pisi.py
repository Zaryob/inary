#!/usr/bin/python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import sys
import re
import datetime

sys.path.insert(0, "/usr/lib/portage/pym")
import portage

PSPEC_TEMPLATE='''<?xml version="1.0" encoding="utf-8" standalone="no"?>

<!DOCTYPE PISI SYSTEM "http://www.uludag.org.tr/projeler/pisi/pisi-spec.dtd">

<PISI>
    <Source>
        <Name>%(packagename)s</Name>
        <Homepage>%(homepage)s</Homepage>
        <Packager>
            <Name>PACKAGER</Name>
            <Email>PACKAGER_EMAIL</Email>
        </Packager>
        <License>%(license)s</License>
        <IsA></IsA>
        <PartOf></PartOf>
        <Summary xml:lang="en">%(description)s</Summary>
        <Description xml:lang="en">%(description)s</Description>
        <Archive type="%(archiveType)s" sha1sum="SUM">%(archiveUri)s</Archive>
        <Patches>
%(patches)s
        </Patches>
        <BuildDependencies>
%(buildDep)s
        </BuildDependencies>
    </Source>

    <Package>
        <Name>%(packagename)s</Name>
        <RuntimeDependencies>
%(runDep)s
        </RuntimeDependencies>
        <Files>
FILES
            <Path fileType=""></Path>
        </Files>
    </Package>

    <History>
        <Update release="1">
            <Date>%(updateDate)s</Date>
            <Version>%(updateVersion)s</Version>
            <Comment>First release.</Comment>
            <Name>PACKAGER</Name>
            <Email>PACKAGER_EMAIL</Email>
        </Update>
    </History>
</PISI>
'''

def packageVersion(pkg):
    if len(pkg) > 1:
        parts = portage.catpkgsplit(pkg)
        if parts == None:
            return ""

        if parts[3] != 'r0':
            version = parts[2] + "-" + parts[3]
        else:
            version = parts[2]
        return version
    else:
        return False

def getArchiveType(uri):
    if uri.endswith("gz"):
        return "targz"
    elif uri.endswith("bz2"): 
        return "tarbz2"
    elif uri.endswith("tar"):
        return "tar"
    elif uri.endswith("zip"):
        return "zip"
    return "UNKNOWN_TYPE"

def getDepString(deps):
    depString = "Dependencies should be reformated and check for correctness"
    for dep in portage.flatten(portage.tokenize(deps)):
        depString += "\n        <Dependency>"+dep+"</Dependency>"

    return depString


def getPatches(filename, pkgName, version):
    fileObj = open(filename)
    patchList=[]

    # ebuild variables
    rc = re.compile
    dispatcher = { 
         rc("\$\{FILESDIR\}"): "",
         rc('"'): "",
         rc('^/'): "",
         rc("\$\{P\}|\$\{PF\}"): "-".join([pkgName,version]),
         rc("\$\{PN\}"): pkgName
         }

    patched = False
    for line in fileObj:
        line = line.strip()
        if line.startswith('#'):
            continue

        p = rc("\Aepatch ").search(line)
        if not p:
            p = rc("\Apatch ").search(line)
        if p:
            patched = True
            line = line[p.end():]
            for r in dispatcher.keys():
                m = r.search(line)
                while m:
                    line = line[:m.start()] + dispatcher[r] + line[m.end():]
                    m = r.search(line)
    
            patchList.append(line)

    patchString = "Patches should be checked for correctness"
    for patch in patchList:
        patchString += "\n        <Patch>"+patch+"</Patch>"

    return patchString

def main(ebuild):
    dict = {}
    db = portage.portdb
    getKeys = lambda x: db.aux_get(ebuild, [x])
    getKey = lambda x: getKeys(x)[0]

    dict["homepage"] = getKey("HOMEPAGE")
    dict["archiveUri"] = getKey("SRC_URI").split()[0]
    dict["archiveType"] = getArchiveType(dict["archiveUri"])
    dict["packagename"] = portage.catpkgsplit(ebuild)[1]
    dict["license"] = getKey("LICENSE")
    dict["description"] = getKey("DESCRIPTION")
    dict["updateDate"] = datetime.date.today()

    # version & release
    if '-' in packageVersion(ebuild):
        (version, release) = packageVersion(ebuild).split("-")
        release = release.replace("r","")
    else:
        version = packageVersion(ebuild)
        release = ''
    dict["updateVersion"] = version
    dict["updateRelease"] = release

    # buildDep & runDep
    deps = getKeys("DEPEND")
    dict["buildDep"] = getDepString(deps)
    dict["runDep"] = getDepString(getKeys("RDEPEND"))

    # patches
    dict["patches"] = getPatches(db.findname(ebuild),
                                 dict["packagename"],
                                 dict["updateVersion"])

    print PSPEC_TEMPLATE % dict

if __name__ == "__main__":
    usage = """Usage:
PORTDIR=/path/to/portage/overlay %s category/ebuild

Example:
PORTDIR=/trunk/ %s app-admin/fam-2.7.0-r2

You don't have to define PORTDIR if you are converting a package from
the main portage repository.
"""
    try:
        ebuild = sys.argv[1]
    except:
        print usage
        sys.exit(1)

    main(ebuild)

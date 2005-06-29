#!/usr/bin/python

import sys
import os
import datetime

sys.path.insert(0, "/usr/lib/portage/pym")
import portage
from portage import catpkgsplit

def packageVersion(pkg):
    if len(pkg) > 1:
        parts = catpkgsplit(pkg)
        if parts == None:
            return ""

        if parts[3] != 'r0':
            version = parts[2] + "-" + parts[3]
        else:
            version = parts[2]
        return version
    else:
        return False

db = portage.portdb

ebuilds = []
for p in db.cp_all():
    for pv in db.cp_list(p):
        ebuilds.append(pv)

try:
    for pkg in ebuilds:
    
        try:
            homepage, description, license, URI, depend, rdepend = portage.portdb.aux_get(pkg, ["HOMEPAGE", "DESCRIPTION", "LICENSE", "SRC_URI", "DEPEND", "RDEPEND"])
        except KeyError:
            homepage, description, license, URI, depend, rdepend  = "", "", ""
            pass
        
        ''' Package name without version '''
        PackageName = catpkgsplit(pkg)[1]
  
        ''' Category and Package name with version '''
        (category, name) = pkg.split("/")

        ''' Version and release '''
        if '-' in packageVersion(pkg):
            (version, release) = packageVersion(pkg).split("-")
            release = release.replace("r","")
        else:
            version = packageVersion(pkg)
            release = ''

        ''' Type of archieve file '''
        if URI[-2:] == 'gz':
            type = 'targz'
        elif URI[-3:] == 'bz2':
            type = 'tarbz2'
        elif URI[-3:] == 'tar':
            type = 'tar'
        elif URI[-3:] == 'zip':
            type = 'zip'

        ''' Current date '''
        date = datetime.date.today()

        ''' Build Dependencies '''
        buildDep = ""
        for dep in portage.flatten(portage.tokenize(depend)):
            buildDep += "       <Dependency>" + dep + "</Dependency>\n"

        ''' Runtime Dependencies '''
        runDep = ""
        for dep in portage.flatten(portage.tokenize(rdepend)):
            runDep += "         <Dependency>" + dep + "</Dependency>\n"

        template='''<?xml version="1.0" encoding="utf-8" standalone="no"?>

<!DOCTYPE PSPEC SYSTEM "http://www.uludag.org.tr/projeler/pisi/pisi-spec.dtd">

<PISI>
    <Source>
        <Name>%s</Name>
        <Homepage>%s</Homepage>
        <Packager>
            <Name>PACKAGER</Name>
            <Email>PACKAGER_EMAIL</Email>
        </Packager>
        <License>%s</License>
        <IsA>category</IsA>
        <PartOf>component</PartOf>
        <Description>%s</Description>
        <Archive type="%s" sha1sum="SUM">%s</Archive>
        <BuildDependencies>

%s
        </BuildDependencies>
        <History>
            <Update>
                <Date>%s</Date>
                <Version>%s</Version>
                <Release>%s</Release>
            </Update>
        </History>
    </Source>

    <Package>
        <Name>%s</Name>
        <Summary xml:lang="en">%s</Summary>
        <RuntimeDependencies>

%s
        </RuntimeDependencies>
        <Description>%s</Description>
        <Files>FILES</Files>
        <History>
            <Update>
                <Date>%s</Date>
                <Version>%s</Version>
                <Release>%s</Release>
            </Update>
        </History>
  </Package>

</PISI>
''' % ( PackageName, homepage, license, description, type, URI, buildDep, date, version, release, PackageName, description, \
       runDep, description, date, version, release )

        ''' package/a/acpid-1.2.0/acpid.pspec '''
        filename = "packages/" + name[:1] + "/" + name + "/" + name + ".pspec"
        
        try:
            os.mkdir("packages/" + name[:1] + "/" + name )
        except OSError, e:
            print "Directort exist %s" % e
            pass

        ''' Write to file '''
        entry = open( filename, 'w' )
        entry.write( template )
        entry.close()
                                    
except KeyboardInterrupt:
    sys.exit(1)

print "Total: " + str(len(ebuilds)) + " ebuilds has been converted to pspec..."

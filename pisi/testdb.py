# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import fcntl
import types

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.util as util
import pisi.context as ctx
import pisi.db.itembyrepodb as itembyrepodb
import pisi.metadata

class TestDB:
    def __init__(self):
        self.db = itembyrepodb.ItemByRepoDB("packages2")
    
    def addPackage(self):
        a = "Hello World"
        self.db.add_item("hello", a, itembyrepodb.installed)
    
    def getPackage(self, name):
        return self.db.get_item(name, itembyrepodb.installed)
    
    def addAllPackages(self):
        pisi.api.init(write=True)
        packages = pisi.context.installdb.list_installed()
        for name in packages:
            pak = pisi.context.packagedb.get_package(name, itembyrepodb.installed)
            #pisi.context.packagedb.add_package(pak, itembyrepodb.installed)
            #print pak.source.name, pak.installedSize
        pisi.api.finalize()
        
    if __name__ == "__main__":
        t = testdb.TestDB()
        t.addAllPackages()

class PackageInfoDAO:
    def __init__(self, package):
        """
        package : pisi.metadata.Package
        """
        self.summary = package.summary
        self.description = package.description

 
class PackageDAO:
    def __init__(self, package):
        """
        package : pisi.metadata.Package
        """
        #
        #from specfile.Package
        #
        self.name = package.name
        #Summary and description will be in another place
        self.summary = package.summary
        self.description = package.description
        self.isA = package.isA
        self.partOf = package.partOf
        self.license = package.license
        self.icon = package.icon
        #from dependencies.Dependency
        self.packageDependencies = package.packageDependencies
        #String
        self.componentDependencies = package.componentDependencies
        self.files = package.files
        self.conflicts = package.conflicts
        self.providesComar = package.providesComar
        self.additionalFiles = package.additionalFiles
        #List of specfile.UPDATE. History will be in another place
        #self.history = package.history
        #
        #from metadata.Package (This is plain stupid.. classes with same name, extending one another.)
        #
        self.build = package.build
        self.distribution = package.distribution
        self.distributionRelease = package.distributionRelease
        self.architecture = package.architecture
        self.installedSize = package.installedSize
        self.packageSize = package.packageSize
        self.packageHash = package.packageHash
        self.packageURI = package.packageURI
        #Delta (List of metadata.Delta objects)
        #self.deltaPackages = package.deltaPackages
        self.packageFormat = package.packageFormat
        #Expanded from metadata.Source
        self.sourceName = package.source.name
        self.sourceHomepage = package.source.homepage
        #Expanded from specfile.Packager
        self.sourcePackagerName = package.source.packager.name
        self.sourcePackagerEmail = package.source.packager.email

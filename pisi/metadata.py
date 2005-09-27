# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Metadata module provides access to metadata.xml. metadata.xml is
# generated during the build process of a package and used in the
# installation. Package repository also uses metadata.xml for building
# a package index.

# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

import pisi.context as ctx
import pisi.specfile as specfile
from pisi.xmlfile import *
from pisi.util import Checks

class SourceInfo:

    def __init__(self, node=None):
        if node:
            self.name = getNodeText(node, "Name")
            self.homepage = getNodeText(node, "HomePage")
            self.packager = specfile.PackagerInfo(getNode(node, "Packager"))
        else:
            self.homepage = None

    def elt(self, xml):
        node = xml.newNode("Source")
        xml.addTextNodeUnder(node, "Name", self.name)
        if self.homepage:
            xml.addTextNodeUnder(node, "Homepage", self.homepage)
        node.appendChild(self.packager.elt(xml))
        return node

    def has_errors(self):
        if not self.name:
            return [ "SourceInfo should have a Name" ]
        return None


class PackageInfo(specfile.PackageInfo):

    def __init__(self, node = None):
        if node:
            specfile.PackageInfo.__init__(self, node)
            self.version = getNodeText(node, "History/Update/Version")
            self.release = getNodeText(node, "History/Update/Release")
            #FIXME: Support Build No under History/Update/Build
            build_ = getNodeText(node, "Build")
            if build_ != None:
                self.build = int(build_)
            else:
                self.build = None
            self.distribution = getNodeText(node, "Distribution")
            self.distributionRelease = getNodeText(node, "DistributionRelease")
            self.architecture = getNodeText(node, "Architecture")
            self.installedSize = int(getNodeText(node, "InstalledSize"))
            self.packageURI = getNodeText(node, "PackageURI")
        else:
            self.packageURI = None

    def elt(self, xml):
        node = specfile.PackageInfo.elt(self, xml)
        if self.build != None:
            xml.addTextNodeUnder(node, "Build", str(self.build))
        xml.addTextNodeUnder(node, "Distribution", self.distribution)
        xml.addTextNodeUnder(node, "DistributionRelease", self.distributionRelease)
        xml.addTextNodeUnder(node, "Architecture", self.architecture)
        xml.addTextNodeUnder(node, "InstalledSize", str(self.installedSize))
        if self.packageURI:
            xml.addTextNodeUnder(node, "PackageURI", str(self.packageURI))
        return node

    def has_errors(self):
        # FIXME: there should be real error msgs
        # and comment the logic here please, it isn't very clear -gurer
        ret = (specfile.PackageInfo.has_errors(self) == None)
        ret = ret and self.distribution!=None
        ret = ret and self.distributionRelease!=None
        ret = ret and self.architecture!=None and self.installedSize!=None
        if ret:
            return None
        return [ "Some error in package metadata" ]

    def __str__(self):
        s = specfile.PackageInfo.__str__(self)
        return s

class MetaData(XmlFile):
    """Package metadata. Metadata is composed of Specfile and various
    other information. A metadata has two parts, Source and Package."""

    def __init__(self):
        XmlFile.__init__(self, "PISI")

    def from_spec(self, src, pkg):
        self.source = SourceInfo()
        self.source.name = src.name
        self.source.homepage = src.homepage
        self.source.packager = src.packager
        self.package = PackageInfo()
        self.package.name = pkg.name
        self.package.summary = pkg.summary
        self.package.description = pkg.description
        self.package.icon = pkg.icon
        self.package.isa = pkg.isa
        self.package.partof = pkg.partof
        self.package.license = pkg.license
        self.package.runtimeDeps = pkg.runtimeDeps
        self.package.paths = pkg.paths
        self.package.history = src.history # FIXME
        self.package.conflicts = pkg.conflicts
        self.package.providesComar = pkg.providesComar
        self.package.requiresComar = pkg.requiresComar
        self.package.additionalFiles = pkg.additionalFiles

        # FIXME: right way to do it?
        self.source.version = src.version
        self.source.release = src.release
        self.package.version = src.version
        self.package.release = src.release

    def read(self, filename):
        self.readxml(filename)
        self.source = SourceInfo(self.getNode("Source"))
        self.package = PackageInfo(self.getNode("Package"))

    def write(self, filename):
        self.newDOM()
        self.addChild(self.source.elt(self))
        self.addChild(self.package.elt(self))
        self.writexml(filename)

    def has_errors(self):
        err = Checks()
        # FIXME: is this an internal error?? -gurer
        if not hasattr(self, 'source'):
            err.add("Metadata should have source")
        err.join(self.source.has_errors())
        
        if not self.package:
            err.add("Metadata should have a package")
        err.join(self.package.has_errors())
        return err.list

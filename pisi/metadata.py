# Metadata module provides access to metadata.xml. metadata.xml is
# generated during the build process of a package and used in the
# installation. Package repository also uses metadata.xml for building
# a package index.
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

from ui import ui

from xmlfile import *
import specfile

class SourceInfo:

    def __init__(self, node=None):
        if node:
            self.name = getNodeText(node, "Name")
            self.homepage = getNodeText(node, "HomePage")
            self.packager = specfile.PackagerInfo(getNode(node, "Packager"))

    def elt(self, xml):
        node = xml.newNode("Source")
        xml.addTextNodeUnder(node, "Name", self.name)
        if self.homepage:
            xml.addTextNodeUnder(node, "Homepage", self.homepage)
        node.appendChild(self.packager.elt(xml))
        return node

    def verify(self):
        ret = True
        ret &= self.name
        return True

class PackageInfo(specfile.PackageInfo):

    def __init__(self, node=None):
        if node:
            specfile.PackageInfo.__init__(self, node)
            self.distribution = getNodeText(node, "Distribution")
            self.distributionRelease = getNodeText(node, "DistributionRelease")
            self.architecture = getNodeText(node, "Architecture")
            self.installedSize = int(getNodeText(node, "InstalledSize"))

    def elt(self, xml):
        node = specfile.PackageInfo.elt(self, xml)
        xml.addTextNodeUnder(node, "Distribution", self.distribution)
        xml.addTextNodeUnder(node, "DistributionRelease", self.distributionRelease)
        xml.addTextNodeUnder(node, "Architecture", self.architecture)
        xml.addTextNodeUnder(node, "InstalledSize", str(self.installedSize))
        return node

    def verify(self):
        ret = True
        ret &= specfile.PackageInfo.verify()
        return True

class MetaData(XmlFile):
    """Package metadata. Metadata is composed of Specfile and various
    other information. A metadata has two parts, Source and Package."""

    def __init__(self):
        XmlFile.__init__(self,"PISI")

    def fromSpec(self, src, pkg):
        self.source = SourceInfo()
        self.source.name = src.name
        self.source.homepage = src.homepage
        self.source.packager = src.packager
        self.package = PackageInfo()
        self.package.name = pkg.name
        self.package.summary = pkg.summary
        self.package.description = pkg.description
        self.package.isa = pkg.isa
        self.package.partof = pkg.partof
        self.package.license = pkg.license
        self.package.installDeps = pkg.installDeps
        self.package.runtimeDeps = pkg.runtimeDeps
        self.package.paths = pkg.paths
        self.package.history = src.history # FIXME

    def read(self, filename):
        self.readxml(filename)
        self.source = SourceInfo(self.getNode("Source"))
        self.package = PackageInfo(self.getNode("Package"))
        self.package.version = self.package.history[0].version
        self.package.release = self.package.history[0].release

    def write(self, filename):
        self.newDOM()
        self.addChild(self.source.elt(self))
        self.addChild(self.package.elt(self))
        self.writexml(filename)

    def verify(self):
        ret = True
        ret &= hasattr(self, 'source')
        if self.source:
            ret &= self.source.verify()
        ret &= self.package != None
        if self.package:
            ret &= self.package.verify()
        return True

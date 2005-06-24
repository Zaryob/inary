
from ui import ui

from xmlfile import *
import specfile

class SourceInfo:
    def __init__(self, node):
        self.name = getNodeText(node, "Name")
        self.homepage = getNodeText(node, "HomePage")
        self.packager = specfile.PackagerInfo(getNode(node, "Packager"))

    def elt(self, xml):
        node = xml.newNode("Source")
        xml.addTextNodeUnder(node, "Name", self.name)
        if self.homepage:
            xml.addTextNodeUnder(node, "Homepage", self.homepage)
        xml.addNodeUnder(node, "", self.packager.elt(xml))
        return node

class PackageInfo(specfile.PackageInfo):

    def __init__(self, node):
        specfile.PackageInfo.__init__(self, node)
        self.distribution = getNodeText(node, "Distribution")
        self.distributionRelease = getNodeText(node, "DistributionRelease")
        self.architecture = getNodeText(node, "Architecture")

        istext = getNodeText(node, "InstalledSize")
        if istext:
            self.installedSize = int(istext)

class MetaData(XmlFile):
    """Package metadata. Metadata is composed of Specfile and various
    other information."""

    def __init__(self):
        XmlFile.__init__(self,"PISI")

    def fromSpec(src, pkg):
        md = MetaData()
        md.source.name = src.source.name
        md.source.homepage = src.source.homepage
        md.source.packager = src.source.packager
        md.package = src.package
        md.package.history = self.source.history # FIXME
        return md

    def read(self, filename):
        self.readxml(filename)
        self.source = SourceInfo(self.getNode("Source"))
        self.package = PackageInfo(self.getNode("Package"))
        self.package.version = self.package.history[0].version
        self.package.release = self.package.history[0].release

    def write(self, filename):
        self.newDOM()
        self.addNode("", self.source.elt(self))
        self.addNode("", self.package.elt(self))
        self.writexml(filename)

    def verify(self):
        assert self.getAllNodes("Package")==1
        assert self.source.name != None
        assert self.source.homepage != None
        assert self.source.packager != None
        return True

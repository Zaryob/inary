# -*- coding: utf-8 -*-
# read/write PISI source package specification file

import xml.dom.minidom
from xmlfile import *
from os.path import basename
from ui import ui

class PatchInfo:
    def __init__(self, filenm, ctype):
        self.filename = filenm
        self.compressionType = ctype

    def __init__(self, node):
        self.filename = getNodeText(node)
        self.compressionType = getNodeAttribute(node, "compressionType")

class DepInfo:
    def __init__(self, node):
        self.package = getNodeText(node).strip()
        self.versionFrom =  getNodeAttribute(node, "versionFrom")

class HistoryInfo:
    def __init__(self, node):
        self.date = getNodeText(getNode(node, "Date"))
        self.version = getNodeText(getNode(node, "Version"))
        self.release = getNodeText(getNode(node, "Release"))

class PathInfo:
    def __init__(self, node):
        self.pathname = getNodeText(node)
        self.fileType = getNodeAttribute(node, "fileType")

# a structure to hold source information
class SourceInfo:
    pass

class PackageInfo:
    def __init__(self, node):
        self.name = getNodeText(getNode(node, "Name"))
        self.summary = getNodeText(getNode(node, "Summary"))
        self.description = getNodeText(getNode(node, "Description"))
        self.category = getNodeText(getNode(node, "Category"))
        iDepElts = getAllNodes(node, "InstallDependencies")
        self.installDeps = [DepInfo(x) for x in iDepElts]
        rtDepElts = getAllNodes(node, "RuntimeDependencies")
        self.runtimeDeps = [DepInfo(x) for x in rtDepElts]
        self.paths = [PathInfo(x) for x in getAllNodes(node, "Files/Path")]

class SpecFile(XmlFile):
    """A class for reading/writing from/to a PSPEC (PISI SPEC) file."""

    def __init__(self):
        XmlFile.__init__(self,"PSPEC")

    def read(self, filename):
        """Read PSPEC file"""
        
        self.readxml(filename)

        self.source = SourceInfo()
        self.source.name = self.getChildText("Source/Name")
        archiveNode = self.getNode("Source/Archive")
        self.source.archiveUri = getNodeText(archiveNode).strip()
        self.source.archiveName = basename(self.source.archiveUri)
        self.source.archiveType = getNodeAttribute(archiveNode, "archType")
        self.source.archiveSHA1 = getNodeAttribute(archiveNode, "sha1sum")
        patchElts = self.getChildElts("Source/Patches")
        if patchElts:
            self.source.patches = [PatchInfo(p) for p in patchElts]

        buildDepElts = self.getChildElts("Source/BuildDependencies")
        if buildDepElts:
            self.source.buildDeps = [DepInfo(d) for d in buildDepElts]

        historyElts = self.getAllNodes("History/Update")
        self.source.history = [HistoryInfo(x) for x in historyElts]

        # As we have no Source/Version tag we need to get 
        # the last version and release information
        # from the first child of History/Update. And it works :)
        self.source.version = self.source.history[0].version
        self.source.release = self.source.history[0].release

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        self.packages = [PackageInfo(p) for p in packageElts]

        self.unlink()
        
    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.newDOM()
        ##TODO: write the good stuff here
        self.writexml(filename)

class MetaData(SpecFile):
    """This is a superset of the source spec definition"""

    def read(self, filename):
        super(MetaData, self).read(filename)
        distribution = self.getNodeText("Source/Distribution")
        distributionRelease = self.getNodeText("Source/DistributionRelease")
        architecture = self.getNodeText("Source/Architecture")
        installSize = int(self.getNodeText("Source/InstallSize"))

    def write(self, filename):
        ui.info("METADATA WRITE NOT IMPLEMENTED\n")
        pass

    def verify():
        if len(packages) != 1:
            return False
        return True


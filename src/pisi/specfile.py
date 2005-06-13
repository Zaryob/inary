# -*- coding: utf-8 -*-
# read/write PISI source package specification file

import xml.dom.minidom
from xmlfile import *

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

class PathInfo:
    def __init__(self, node):
        self.pathname = getNodeText(node)
        self.fileType = getNodeAttribute(node, "fileType")

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
        self.sourceName = self.getChildText("Source/Name")
	archiveNode = self.getNode("Source/Archive")
        self.archiveUri = getNodeText(archiveNode).strip()
	self.archiveType = getNodeAttribute(archiveNode, "archType")
	self.archiveMD5 = getNodeAttribute(archiveNode, "md5sum")
        patchElts = self.getChildElts("Source/Patches")
        self.patches = [ PatchInfo(p) for p in patchElts ]

        buildDepElts = self.getChildElts("Source/BuildDependencies")
        self.buildDeps = [DepInfo(d) for d in buildDepElts]

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        self.packages = [PackageInfo(p) for p in packageElts]
            
    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.writexml(filename)

class MetaData(SpecFile):
    """This is a superset of the source spec definition"""

    def read(self, filename):
        SpecFile.read(filename)
	distribution = self.getNodeText("Source/Distribution")
	distributionRelease = self.getNodeText("Source/DistributionRelease")
	architecture = self.getNodeText("Source/Architecture")
	installSize = self.getNodeText("Source/InstallSize")


# -*- coding: utf-8 -*-
# read/write PISI source package specification file

import xml.dom.minidom
from xmlext import *
from xmlfile import XmlFile
from os.path import basename
from ui import ui

class PatchInfo:
    def __init__(self, filenm, ctype):
        self.filename = filenm
        self.compressionType = ctype

    def __init__(self, node):
        self.filename = getNodeText(node)
        self.compressionType = getNodeAttribute(node, "compressionType")

    def addNode(self, xml):
        node = xml.addNode("Source/Patches/Patch")
        node.setAttribute("filename", self.filename)
        node.setAttribute("compressionType", self.compressionType)

class DepInfo:
    def __init__(self, node):
        self.package = getNodeText(node).strip()
        self.versionFrom = getNodeAttribute(node, "versionFrom")
        self.versionTo = getNodeAttribute(node, "versionTo")

    def elt(self, xml):
        node = xml.newNode("Dependency")
        node.setAttribute("versionFrom", self.versionFrom)
        node.setAttribute("versionTo", self.versionTo)
        return node

class UpdateInfo:
    def __init__(self, node):
        self.date = getNodeText(getNode(node, "Date"))
        self.version = getNodeText(getNode(node, "Version"))
        self.release = getNodeText(getNode(node, "Release"))

    def elt(self, xml):
        node = xml.newNode("Update")
        xml.addTextNodeUnder(node, "Date", self.date)
        xml.addTextNodeUnder(node, "Version", self.version)
        xml.addTextNodeUndeR(node, "Release", self.release)
        return node

class PathInfo:
    def __init__(self, node):
        self.pathname = getNodeText(node)
        self.fileType = getNodeAttribute(node, "fileType")

    def elt(self, xml):
        node = xml.newNode("Path")
        xml.addText(node, self.pathname)
        node.setAttribute("fileType", self.fileType)
        return node

# a structure to hold source information
class SourceInfo:
    pass

class PackageInfo:
    def __init__(self, node):
        self.name = getNodeText(getNode(node, "Name"))
        self.summary = getNodeText(getNode(node, "Summary"))
        self.description = getNodeText(getNode(node, "Description"))
        self.category = getNodeText(getNode(node, "Category"))
        iDepElts = getAllNodes(node, "InstallDependencies/Dependency")
        self.installDeps = [DepInfo(x) for x in iDepElts]
        rtDepElts = getAllNodes(node, "RuntimeDependencies/Dependency")
        self.runtimeDeps = [DepInfo(x) for x in rtDepElts]
        self.paths = [PathInfo(x) for x in getAllNodes(node, "Files/Path")]

    def elt(self, xml):
        node = xml.newNode("Package")
        xml.addTextNodeUnder(node, "Name", self.name)
        xml.addTextNodeUnder(node, "Summary", self.summary)
        xml.addTextNodeUnder(node, "Description", self.description)
        xml.addTextNodeUnder(node, "Category", self.category)
        
        return node
        
class SpecFile(XmlFile):
    """A class for reading/writing from/to a PSPEC (PISI SPEC) file."""

    def __init__(self):
        XmlFile.__init__(self,"PSPEC")

    def read(self, filename):
        """Read PSPEC file"""
        
        self.readxml(filename)

        self.source = SourceInfo()
        self.source.name = self.getChildText("Source/Name")
        self.source.license = self.getChildText("Source/License")
        archiveNode = self.getNode("Source/Archive")
        self.source.archiveUri = getNodeText(archiveNode).strip()
        self.source.archiveName = basename(self.source.archiveUri)
        self.source.archiveType = getNodeAttribute(archiveNode, "archType")
        self.source.archiveSHA1 = getNodeAttribute(archiveNode, "sha1sum")
        patchElts = self.getAllNodes("Source/Patches/Patch")
        self.source.patches = [PatchInfo(p) for p in patchElts]
        buildDepElts = self.getAllNodes("Source/BuildDependencies/Dependency")
        self.source.buildDeps = [DepInfo(d) for d in buildDepElts]
        historyElts = self.getAllNodes("History/Update")
        self.source.history = [UpdateInfo(x) for x in historyElts]

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
        self.addTextNode("Source/Name", self.source.name)
        archiveNode = self.addNode("Source/Archive")
        archiveNode.setAttribute("archType", self.source.archiveType)
        archiveNode.setAttribute("sha1sum", self.source.archiveSHA1)
        for patch in self.source.patches:
            patch.addNode(self)
        for dep in map(lambda x : x.elt(self), self.source.buildDeps):
            self.addNode("Source/BuildDependencies", dep)
        self.writexml(filename)

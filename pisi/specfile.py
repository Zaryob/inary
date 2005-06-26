# -*- coding: utf-8 -*-

# Specfile module is our handler for PSPEC files. PSPEC (PISI SPEC)
# files are specification files for PISI source packages. This module
# provides read and write access to PSPEC files.

# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

# standard python modules
import xml.dom.minidom
from os.path import basename

# pisi modules
from xmlext import *
from xmlfile import XmlFile
from ui import ui

class PackagerInfo:
    def __init__(self, node):
        self.name = getNodeText(getNode(node, "Name"))
        self.email = getNodeText(getNode(node, "Email"))

    def elt(self, xml):
        node = xml.newNode("Packager")
        xml.addTextNodeUnder(node, "Name", self.name)
        xml.addTextNodeUnder(node, "Email", self.email)
        return node

class PatchInfo:
    def __init__(self, filenm, ctype):
        self.filename = filenm
        self.compressionType = ctype

    def __init__(self, node):
        self.filename = getNodeText(node)
        self.compressionType = getNodeAttribute(node, "compressionType")

    def elt(self, xml):
        node = xml.newNode("Patch")
        node.setAttribute("filename", self.filename)
        if self.compressionType:
            node.setAttribute("compressionType", self.compressionType)
        return node

class DepInfo:
    def __init__(self, node):
        self.package = getNodeText(node).strip()
        self.versionFrom = getNodeAttribute(node, "versionFrom")
        self.versionTo = getNodeAttribute(node, "versionTo")

    def elt(self, xml):
        node = xml.newNode("Dependency")
        xml.addText(node, self.package)
        if self.versionFrom:
            node.setAttribute("versionFrom", self.versionFrom)
        if self.versionTo:
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
        xml.addTextNodeUnder(node, "Release", self.release)
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

class SourceInfo:
    """A structure to hold source information. Source information is
    located under <Source> tag in PSPEC file."""
    def __init__(self, node):
        self.name = getNodeText(node, "Name")
        self.homepage = getNodeText(node, "HomePage")
        self.packager = PackagerInfo(getNode(node, "Packager"))
        self.description = getNodeText(node, "Description")
        self.license = getNodeText(node, "License")
        self.isa = getNodeText(node, "IsA")
        self.partof = getNodeText(node, "PartOf")
        archiveNode = getNode(node, "Archive")
        self.archiveUri = getNodeText(archiveNode).strip()
        self.archiveName = basename(self.archiveUri)
        self.archiveType = getNodeAttribute(archiveNode, "archType")
        self.archiveSHA1 = getNodeAttribute(archiveNode, "sha1sum")
        patchElts = getAllNodes(node, "Patches/Patch")
        self.patches = [PatchInfo(p) for p in patchElts]
        buildDepElts = getAllNodes(node, "BuildDependencies/Dependency")
        self.buildDeps = [DepInfo(d) for d in buildDepElts]
        historyElts = getAllNodes(node, "History/Update")
        self.history = [UpdateInfo(x) for x in historyElts]

    def elt(self, xml):
        node = xml.newNode("Source")
        xml.addTextNodeUnder(node, "Name", self.name)
        if self.homepage:
            xml.addTextNodeUnder(node, "Homepage", self.homepage)
        node.appendChild(self.packager.elt(xml))
        xml.addTextNodeUnder(node, "Description", self.description)
        xml.addTextNodeUnder(node, "License", self.license)
        xml.addTextNodeUnder(node, "IsA", self.isa)
        xml.addTextNodeUnder(node, "PartOf", self.partof)
        archiveNode = xml.addNodeUnder(node, "Archive")
        archiveNode.setAttribute("archType", self.archiveType)
        archiveNode.setAttribute("sha1sum", self.archiveSHA1)
        for patch in self.patches:
            xml.addNodeUnder(node, "Patches", patch.elt(xml))
        for dep in self.buildDeps:
            xml.addNodeUnder(node, "BuildDependencies", dep.elt(xml))
        for update in self.history:
            xml.addNodeUnder(node, "History", update.elt(xml))
        return node

class PackageInfo:
    """A structure to hold package information. Package information is
    located under <Package> tag in PSPEC file. Opposite to Source each
    PSPEC file can have more than one Package tag."""
    def __init__(self, node):
        self.name = getNodeText(node, "Name")
        self.summary = getNodeText(node, "Summary")
        self.description = getNodeText(node, "Description")
        self.isa = getNodeText(node, "IsA")
        self.partof = getNodeText(node, "PartOf")
        self.license = getNodeText(node, "License")
        iDepElts = getAllNodes(node, "InstallDependencies/Dependency")
        self.installDeps = [DepInfo(x) for x in iDepElts]
        rtDepElts = getAllNodes(node, "RuntimeDependencies/Dependency")
        self.runtimeDeps = [DepInfo(x) for x in rtDepElts]
        self.paths = [PathInfo(x) for x in getAllNodes(node, "Files/Path")]
        historyElts = getAllNodes(node, "History/Update")
        self.history = [UpdateInfo(x) for x in historyElts]

    def elt(self, xml):
        node = xml.newNode("Package")
        xml.addTextNodeUnder(node, "Name", self.name)
        xml.addTextNodeUnder(node, "Summary", self.summary)
        xml.addTextNodeUnder(node, "Description", self.description)
        if self.isa:
            xml.addTextNodeUnder(node, "IsA", self.isa)
        if self.partof:
            xml.addTextNodeUnder(node, "PartOf", self.partof)
        for dep in self.installDeps:
            xml.addNodeUnder(node, "InstallDependencies", dep.elt(xml))
        for dep in self.runtimeDeps:
            xml.addNodeUnder(node, "RuntimeDependencies", dep.elt(xml))
        for path in self.paths:
            xml.addNodeUnder(node, "Files", path.elt(xml))
        for update in self.history:
            xml.addNodeUnder(node, "History", update.elt(xml))
        return node
        
class SpecFile(XmlFile):
    """A class for reading/writing from/to a PSPEC (PISI SPEC) file."""

    def __init__(self):
        XmlFile.__init__(self,"PISI")

    def read(self, filename):
        """Read PSPEC file"""
        
        self.readxml(filename)

        self.source = SourceInfo(self.getNode("Source"))

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
        self.addChild(self.source.elt(self))
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)

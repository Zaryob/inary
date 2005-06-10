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

class PackageInfo:
    def __init__(self, node):
        comps = getChildElts(node)
        self.name = comps[0]

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
	self.archiveHash = getNodeAttribute(archiveNode, "md5sum")
        patchElts = self.getChildElts("Source/Patches")
        patches = [ PatchInfo(p) for p in patchElts ]
        for x in patches:
            print "patch fn:", x.filename
            print "patch ct:", x.compressionType
        buildDepElts = self.getChildElts("Source/BuildDependencies")
        buildDeps = [DepInfo(d) for d in buildDepElts]
        for x in buildDeps:
            print "dep nm:", x.package
            print "dep vf:", x.versionFrom

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        packages = [PackageInfo(p) for p in packageElts]
        print packages
        
    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.writexml(filename)

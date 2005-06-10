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

class SpecFile(XmlFile):
    """A class for reading/writing from/to a PSPEC (PISI SPEC) file."""

    def read(self, filename):
        """Read PSPEC file"""
        self.readxml(filename)
        self.sourceName = self.getChildText("PSPEC/Source/Name")
	archiveNode = self.getNode("PSPEC/Source/Archive")
        self.archiveUri = getNodeText(archiveNode).strip()
	self.archiveType = getNodeAttribute(archiveNode, "archType")
	self.archiveHash = getNodeAttribute(archiveNode, "md5sum")
        patchElts = self.getChildElts("PSPEC/Source/Patches")
        patches = [ PatchInfo(p) for p in patchElts ]
        for x in patches:
            print "fn:", x.filename
            print "ct:", x.compressionType
            
    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.writexml(filename)

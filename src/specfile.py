# -*- coding: utf-8 -*-
# read/write PISI source package specification file

import xml.dom.minidom
from xmlfile import XmlFile

class PatchInfo:
    def __init__(self, filenm, ctype):
        self.filename = filenm
        self.compressionType = ctype

class SpecFile(XmlFile):
    """A class for reading/writing from/to a PSPEC (PISI SPEC) file."""

    def read(self, filename):
        """Read PSPEC file"""
        self.readxml(filename)
        self.sourceName = self.getFirstChildText("PSPEC/Source/Name")
	archiveNode = self.getFirstNode("PSPEC/Source/Archive")
        self.archiveUri = self.getNodeText(archiveNode).strip()
	self.archiveType = self.getNodeAttribute(archiveNode, "archType")
	self.archiveHash = self.getNodeAttribute(archiveNode, "md5sum")
        patches = self.getNode("PSPEC/Source/Patches")
        #patches = self.dom.getElementsByTagName("PSPEC")
        #for x in patc

    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.writexml(filename)

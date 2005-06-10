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
	self.archiveNode = self.getFirstNode("PSPEC/Source/Archive")
        self.sourceName = self.getFirstChildText("PSPEC/Source/Name")
        self.archiveUri = self.getNodeText(self.archiveNode).strip()
	self.archiveType = self.getNodeAttribute(self.archiveNode, "archType")
	self.archiveHash = self.getNodeAttribute(self.archiveNode, "md5sum")

    def verify(self):
        """Verify PSPEC structures, are they what we want of them?"""
        return True
    
    def write(self, filename):
        """Write PSPEC file"""
        self.writexml(filename)

if __name__ == "__main__":
    import sys
    sys.stderr.write("Not a callable module!")
    exit(-1)

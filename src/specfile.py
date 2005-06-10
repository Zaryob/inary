# -*- coding: utf-8 -*-

import xml.dom.minidom
from xmlfile import XmlFile

class PatchInfo:
    def __init__(self, filenm, ctype):
        self.filename = filenm
        self.compressionType = ctype

# sayin arkadaslarim burada write icin koydugum seyleri silmeyin 
# bu tam olmamis duzeltiyorum, o getlere de genel olarak
# ihtiyac yok. *client* icin nasil kolay oluyorsa oyle olmali
# yanlis su: bir class icindeki state'i cache etmez store eder
# cache etmek ne zaman gerekir? represent ettigi data core'a
# sigmiyorsa. diger zamanlarda yanlis bir metod olur.
# otesinde de refactor ediyorum biraz -- eray

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

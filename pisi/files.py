# Files module provides access to files.xml. files.xml is genarated
# during the build process of a package and used in installation.
# Authors:  Eray Ozkural <eray@uludag.org.tr>

from xmlext import *
from xmlfile import XmlFile

class FileInfo:
    """FileInfo holds the information for a File node/tag in files.xml"""
    def __init__(self, _path = "", _type = "", _size = "", _hash = ""):
        self.path = _path
        self.type = _type
        self.size = _size
        self.hash = _hash

    def readnew(node):
        f = FileInfo()
        f.read(node)
        return f
    readnew = staticmethod(readnew)

    def read(self, node):
        self.path = getNodeText(getNode(node, "Path"))
        self.type = getNodeText(getNode(node, "Type"))
        self.size = getNodeText(getNode(node, "Size"))
        self.hash = getNodeText(getNode(node, "SHA1Sum"))

    def elt(self, dom):
        ## FIXME: looking for a better way to do it
        ## could apparently use helper functions to do this shorter
        elt = dom.createElement("File")
        pathElt = dom.createElement("Path")
        pathElt.appendChild(dom.createTextNode(self.path))
        typeElt = dom.createElement("Type")
        typeElt.appendChild(dom.createTextNode(self.type))
        sizeElt = dom.createElement("Size")
        sizeElt.appendChild(dom.createTextNode(self.size))
        hashElt = dom.createElement("SHA1Sum")
        hashElt.appendChild(dom.createTextNode(self.hash))
        elt.appendChild(pathElt)
        elt.appendChild(typeElt)
        elt.appendChild(sizeElt)
        elt.appendChild(hashElt)
        return elt

    def verify(self):
        if not self.path: return False
        if not self.type: return False
        if not self.size: return False
        if not self.hash: return False
        return True

class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")
        self.list = []

    def append(self, fileinfo):
        self.list.append(fileinfo)

    def read(self, filename):
        self.readxml(filename)

        fileElts = self.getAllNodes("File")
        self.list = [FileInfo.readnew(x) for x in fileElts]

    def write(self, filename):
        self.newDOM()
        document = self.dom.documentElement
        for x in self.list:
            document.appendChild(x.elt(self.dom))
        self.writexml(filename)

    def verify(self):
        for finfo in self.list:
            if not finfo.verify(): return False
        return True

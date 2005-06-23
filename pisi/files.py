 # class for files.xml

import xmlfile
from xmlfile import XmlFile


class FileInfo:
    
    def __init__(self, _path = "", _type = "", _size="", _hash = ""):
        self.path = _path
        self.type = _type
        self.size = _size
        self.hash = _hash

    def readnew(node):
        f = FileInfo()
        f.read(node)
        return f

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

class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")
        self.list = []

    def append(self, fileinfo):
        self.list.append(fileinfo)

    def read(self, filename):
        self.readxml(filename)

        fileElts = getAllNodes(node, "File")
        self.list = [FileInfo.readnew(x) for x in fileElts]

    def write(self, filename):
        self.newDOM()
        document = self.dom.documentElement
        for x in self.list:
            document.appendChild(x.elt(self.dom))
        self.writexml(filename)

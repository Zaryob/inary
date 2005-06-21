 # class for files.xml


class FileInfo:
    
    def __init__(self, _path = "", _type = "", _size = 0, _hash = ""):
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
        self.size = int(getNodeText(getNode(node, "Size")))
        self.hash = getNodeText(getNode(node, "Hash"))

    def elt(self, dom):
        ## FIXME: looking for a better way to do it
        ## could apparently use helper functions to do this shorter
        elt = dom.createElement("File")
        pathElt = dom.createElement("Path")
        pathElt.appendChild(dom.createTextNode(path))
        typeElt = dom.createElement("Type")
        typeElt.appendChild(dom.createTextNode(type))
        sizeElt = dom.createElement("Size")
        sizeElt.appendChild(dom.createTextNode(str(size)))
        hashElt = dom.createElement("Hash")
        hashElt.appendChild(dom.createTextNode(hash))
        elt.appendChild(pathElt)
        elt.appendChild(typeElt)
        elt.appendChild(sizeElt)
        elt.appendChild(hashElt)
        return elt

class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")

    def read(self, filename):
        self.readxml(filename)

        fileElts = getAllNodes(node, "File")
        self.list = [FileInfo.readnew(x) for x in fileElts]

    def write(self, filename):
        self.newDOM()
        for x in list:
            self.appendChild(x.elt(self.dom))
            


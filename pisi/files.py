 # class for files.xml


class FileInfo:
    
    def __init__(self, node):
        self.path = getNodeText(getNode(node, "Path"))
        self.type = getNodeText(getNode(node, "Type"))
        self.size = int(getNodeText(getNode(node, "Size")))
        self.md5Sum = getNodeText(getNode(node, "MD5Sum"))

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
        md5Elt = dom.createElement("MD5Sum")
        md5Elt.appendChild(dom.createTextNode(md5sum))
        elt.appendChild(pathElt)
        elt.appendChild(typeElt)
        elt.appendChild(sizeElt)
        elt.appendChild(md5Elt)
        return elt

class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")

    def read(self, filename):
        self.readxml(filename)

        fileElts = getAllNodes(node, "File")
        self.list = [FileInfo(x) for x in fileElts]

    def write(self, filename):
        self.newDOM()
        for x in list:
            self.appendChild(x.elt(self.dom))
            



# reader for files.xml


class FileInfo:
    
    def __init__(self, node):
        self.path = getNodeText(getNode(node, "Path"))
        self.type = getNodeText(getNode(node, "Type"))
        self.size = int(getNodeText(getNode(node, "Size")))
        self.md5Sum = getNodeText(getNode(node, "MD5Sum"))

    def elt(self, dom):
        ## FIXME: looking for the clean way to do it
        elt = dom.createElement()
        elt.appendChild(dom.createTextNode(path))
        elt.appendChild(dom.createTextNode(type))
        elt.appendChild(dom.createTextNode(size))
        elt.appendChild(dom.createTextNode(size))
        return elt

class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")

    def read(self, filename):
        self.readxml(filename)

        fileElts = getAllNodes(node, "File")
        self.list = [FileInfo(x) for x in fileElts]

    def write(self, filename):
        #FIXME: need a function to clear DOM first!
        for x in list:
            pass
            #elf.putNode("File/
            


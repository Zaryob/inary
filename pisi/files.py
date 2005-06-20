
# reader for files.xml


class FileInfo:
    def __init__(self, node):
        self.path = getNodeText(getNode(node, "Path"))
        self.type = getNodeText(getNode(node, "Type"))
        self.size = int(getNodeText(getNode(node, "Size")))
        self.md5Sum = getNodeText(getNode(node, "MD5Sum"))


class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")

    def read(self, filename):
        self.readxml(filename)

        fileElts = getAllNodes(node, "File")
        self.installDeps = [FileInfo(x) for x in fileElts]

    def write(self, filename):
        pass


# -*- coding: utf-8 -*-

import xml.dom.minidom

class SpecFile:
    """SpecFile: A class for extracting specific information
from a PSPEC file"""
    def __init__(self, specfile):
        self.filename = specfile

    def read():
	self.dom = xml.dom.minidom.parse(filename)
        # fill in fields
        
        self.packageName = pspec.getFirstChildText("Source/Name")

	archiveNode = pspec.getFirstNode("Source/Archive")
	self.archiveUri = pspec.getNodeText(archiveNode).strip()
	self.archiveName = basename(self.archiveUri)
	self.archiveType = pspec.getNodeAttribute(archiveNode, "archType")
	self.archiveHash = pspec.getNodeAttribute(archiveNode,
                                                  "md5sum")
        patchesnode = pspec.getFirstNode("Source/Patches")

    def write(outfn):
        f = file(outfn, 'w')
        xml.dom.minidom.writexml(f)

    def getNodes(self, nodepath):
	"""getNodes function return nodes for given path of the node.
	getNodes("Source/Name")
	returns a list of nodes in PSPEC/Source"""
        nodepath = "PSPEC/" + nodepath
	nodeArray=nodepath.split('/')

	# get DOM for top node
	nodelist = self.dom.getElementsByTagName(nodeArray[0])
	# iterate over
	for nodename in nodeArray[1:]:
	    nodelist = nodelist[0].getElementsByTagName(nodename)
	
	return nodelist

    def getFirstNode(self, nodepath):
        nodepath = "PSPEC/" + nodepath
	try:
	    return self.getNodes(nodepath)[0]
	except IndexError:
	    return None
    
    def getNodeText(self, node):
	# get the first child
	try:
	    child = node.childNodes[0]
	except IndexError:
	    return None

	if child.nodeType == child.TEXT_NODE:
	    return child.data

    def getFirstChildText(self, nodepath):
        nodepath = "PSPEC/" + nodepath
	node = self.getFirstNode(nodepath)
	if not node:
	    return None

	return self.getNodeText(node)
    
    def getNodeAttribute(self, node, attrname):
	for i in range(node.attributes.length):
	    attr = node.attributes.item(i)
	    if attr.name == attrname:
		return attr.childNodes[0].data

if __name__ == "__main__":
    import sys
    sys.stderr.write("Not a callable module!")

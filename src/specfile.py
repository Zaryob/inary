# -*- coding: utf-8 -*-

import xml.dom.minidom

class SpecFile:
    """SpecFile: A class for extracting specific information
from a PSPEC file"""
    def __init__(self, specfile):
	self.dom = xml.dom.minidom.parse(specfile)

    def getNodes(self, nodepath):
	"""getNodes function return nodes for given path of the node.
	getNodes("PSPEC/Source/Name")
	returns an array of Name tags in PSPEC/Source"""
	nodeArray=nodepath.split('/')

	
	# get DOM for top node
	nodelist = self.dom.getElementsByTagName(nodeArray[0])
	# iterate over
	for nodename in nodeArray[1:]:
	    nodelist = nodelist[0].getElementsByTagName(nodename)
	
	return nodelist

    def getFirstNode(self, nodepath):
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

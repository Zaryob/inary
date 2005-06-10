# some helper functions for using minidom

import xml.dom.minidom

class XmlError(Exception):
    pass

class XmlFile(object):
    """A class for retrieving information from an XML file"""

    def readxml(self, filenm):
	self.dom = xml.dom.minidom.parse(filenm)

    def writexml(self, filenm):
        f = file(filenm,'w')
        self.dom.writexml(f)

    def getChildren(self, tagpath):
        """ returns the children of the given path"""
        return self.dom.getChildren()

    def getNode(self, tagpath):
	"""returns the node for given *unique* path of the node.

	getNode("PSPEC/Source")
	returns the node with the tag path PSPEC/Source"""

	tags=tagpath.split('/')

        # code to search for the path

	# get DOM for top node
	nodelist = self.dom.getElementsByTagName(tags[0])

        if len(nodelist)==0:
            raise XmlError("Root tag for " % tagpath % " not found")

        node = nodelist[0]              # discard other matches
	for nodename in tags[1:]:
	    nodelist = node.getElementsByTagName(nodename)
            if len(nodelist)==0:
                raise XmlError("Tag path " % tagpath % " broken")
            else:
                node = nodelist[0]

	return node

    def getAllNodes(self, nodepath):
	"""returns all trees corresponding to given path.

	getAllNodes("PSPEC/Source")
	returns an array of nodes under PSPEC/Source"""
        raise XmlError("Not implemented!")

    def getFirstNode(self, nodepath):
	try:
	    return self.getNode(nodepath)
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

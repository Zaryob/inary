# -*- coding: utf-8 -*-

import xml.dom.minidom

class XmlFile(object):
    """A class for retrieving information from an XML file"""

    def __init__(self, specfile):
	self.dom = xml.dom.minidom.parse(specfile)

    def getNodes(self, nodepath):
	"""getNodes function return nodes for given path of the node.

	getNodes("PSPEC/Source/Name")
	returns an array of Name nodes in PSPEC/Source"""

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


class SpecFile(XmlFile):
    """A class for retrieving specific information from a
    PSPEC (PISI SPEC) file.

    Information retrieved from PSPEC file is cached (where possible)
    once accessed, for further usage.
    """

    def __init__(self, specfile):
	super(SpecFile, self).__init__(specfile)

	self.archiveNode = self.getFirstNode("PSPEC/Source/Archive")

    def getSourceName(self):
	try:
	    return self.sourceName
	except AttributeError:
	    print "buraya yalnızca bir defa gelebilirsin..."
	    self.sourceName = self.getFirstChildText("PSPEC/Source/Name")
	    return self.sourceName

    def getArchiveUri(self):
	try:
	    return self.archiveUri
	except AttributeError:
	    self.archiveUri = self.getNodeText(self.archiveNode).strip()
	    return self.archiveUri

    def getArchiveType(self):
	return self.getNodeAttribute(self.archiveNode, "archType")

    def getArchiveHash(self):
	return self.getNodeAttribute(self.archiveNode, "md5sum")


if __name__ == "__main__":
    import sys
    sys.stderr.write("Not a callable module!")

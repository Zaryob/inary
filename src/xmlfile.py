# -*- coding: utf-8 -*-
# some helper functions for using minidom

import xml.dom.minidom as mdom

class XmlError(Exception):
    pass

# static functions

def getNodeAttribute(node, attrname):
    for i in range(node.attributes.length):
        attr = node.attributes.item(i)
        if attr.name == attrname:
            return attr.childNodes[0].data

def getNodeText(node):
    # get the first child
    try:
        child = node.childNodes[0]
    except IndexError:
        return None
    if child.nodeType == child.TEXT_NODE:
        return child.data
    else:
        raise XmlError("getNodeText: Expected text node, got something else!")

# xmlfile class that further abstracts a dom object

class XmlFile(object):
    """A class for retrieving information from an XML file"""

    def readxml(self, filenm):
	self.dom = mdom.parse(filenm)

    def writexml(self, filenm):
        f = file(filenm,'w')
        self.dom.writexml(f)

    def getChildren(self, tagpath):
        """ returns the children of the given path"""
        node = self.getNode(tagpath)
        return node.childNodes

    # get only elements of a given type
    # BUG: this doesn't work
    def getChildrenWithType(self, tagpath, type):
        """ returns the children of the given path, only with given type """
        node = self.getNode(tagpath)
        return filter(lambda x:x.nodeType==type, node.childNodes)

    # get only child elements, slightly better than Serdar's sol'n :> -- exa
    def getChildElts(self, tagpath):
        """ returns the children of the given path, only with given type """
        node = self.getNode(tagpath)
        return filter(lambda x:x.nodeType==x.ELEMENT_NODE, node.childNodes)

    def getNode(self, tagpath):
	"""returns the node for given *unique* path of the node.

	getNode("PSPEC/Source")
	returns the node with the tag path PSPEC/Source"""

	tags=tagpath.split('/')

        # code to search for the path

	# get DOM for top node
	nodelist = self.dom.getElementsByTagName(tags[0])

        if len(nodelist)==0:
            return None                 # not found

        node = nodelist[0]              # discard other matches
	for nodename in tags[1:]:
	    nodelist = node.getElementsByTagName(nodename)
            if len(nodelist)==0:
                return None
            else:
                node = nodelist[0]

        return node

    def getAllNodes(self, nodepath):
	"""returns all trees corresponding to given path.

	getAllNodes("PSPEC/Source")
	returns an array of nodes under PSPEC/Source"""
        raise XmlError("Not implemented!")

    def getChildText(self, tagpath):
	node = self.getNode(tagpath)
	if not node:
	    return None

	return getNodeText(node)


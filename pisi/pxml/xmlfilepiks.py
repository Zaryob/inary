# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Gurer Ozen <gurer@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

"""
 XmlFile class further abstracts a dom object using the
 high-level dom functions provided in xmlext module

 this implementation uses piksemel, a fast C-based XML library
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
from piksemel import *

class Error(pisi.Error):
    "named this way because the class if mostly used with an import *"
    pass

class XmlFile(object):
    """A class to help reading and writing an XML file"""

    def __init__(self, tag):
        self.rootTag = tag
        self.newDocument()

    def newDocument(self):
        """clear DOM"""
        self.doc = newDocument(self.rootTag)

    def unlink(self):
        """deallocate DOM structure"""
        pass # piksemel is garbage collected!

    def rootNode(self):
        """returns root document element"""
        return self.doc

    def readxml(self, fileName):
        try:
            self.doc = parse(fileName)
        except ParseError, inst:
            raise XmlError(_("File '%s' has invalid XML: %s\n") % (fileName,
                                                                   str(inst)))

    def writexml(self, fileName):
        f = codecs.open(fileName,'w', "utf-8")
        f.write(self.doc.toPrettyString())
        f.close()

    def verifyRootTag(self):
        actual_roottag = self.rootNode().tagName
        if actual_roottag != self.rootTag:
            raise Error(_("Root tagname %s not identical to %s as expected") %
                        (actual_roottag, self.rootTag) )

    # construction helpers

    #def newNode(self, tag):
    #    return self.dom.createElement(tag)

    #def newTextNode(self, text):
    #    return self.dom.createTextNode(text)

    #def newAttribute(self, attr):
    #    return self.dom.createAttribute(attr)

    # read helpers

    def getNode(self, tagPath = ""):
        """returns the *first* matching node for given tag path."""
        self.verifyRootTag()
        return getNode(self.doc, tagPath)

    def getNodeText(self, tagPath):
        """returns the text of *first* matching node for given tag path."""
        node = self.getNode(tagPath)
        if not node:
            return None
        return getNodeText(node)

    def getAllNodes(self, tagPath):
        """returns all nodes matching a given tag path."""
        self.verifyRootTag()
        return getAllNodes(self.doc, tagPath)

    def getChildren(self, tagpath):
        """ returns the children of the given path"""
        node = self.getNode(tagpath)
        return [x for x in parent.childNodes]

    # get only child elements
    def getChildElts(self, tagpath):
        """ returns the children of the given path, only with given type """
        return getChildElts(self.getNode(tagpath))

    # write helpers

    def addNode(self, tagPath, newnode = None):
        "this adds the newnode under given tag path"
        self.verifyRootTag()
        return addNode(self.doc, tagPath, newnode)

    def addNodeUnder(self, node, tagPath, newnode = None):
        "this adds the new stuff under node and then following tag path"
        self.verifyRootTag()
        return addNode(node, tagPath, newnode)

    def addChild(self, newnode):
        "add a new child node right under root element document"
        self.dom.documentElement.appendChild(newnode)

    def addText(self, node, text):
        "add text to node"
        raise Error('NOT IMPLEMENTED')
        #node.appendChild(self.newTextNode(text))

    def addTextNode(self, tagPath, text):
        "add a text node with given tag path"
        raise Error('NOT IMPLEMENTED')
        #node = self.addNode(tagPath, self.newTextNode(text))
        #return node

    def addTextNodeUnder(self, node, tagPath, text):
        "add a text node under given node with tag path (phew)"
        raise Error('NOT IMPLEMENTED')
        #return self.addNodeUnder(node, tagPath, self.newTextNode(text))

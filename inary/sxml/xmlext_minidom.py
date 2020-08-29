# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""
 xmlext is a helper module for accessing XML files using
 xml.dom.minidom . It is a convenient wrapper for some
 DOM functions, and provides path based get/add functions
 as in KDE API.

 function names are mixedCase for compatibility with minidom,
 an 'old library'

 this implementation uses minidom
"""

# MiniDOM Library
# in order to lack possibility of Ciksemel
from xml.parsers.expat import ExpatError
import xml.dom.minidom as minidom

# Inary Modules
import inary.errors

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class XMLError(inary.errors.Error):
    pass


def newDocument(tag):
    impl = minidom.getDOMImplementation()
    dom = impl.createDocument(None, tag, None)
    return dom.documentElement


def parse(fileName):
    try:
        dom = minidom.parse(fileName)
        return dom.documentElement
    except ExpatError as inst:
        raise XMLError(_("File \"{}\" has invalid XML: {}\n").format(fileName,
                                                                     str(inst)))


def parseString(fileString):
    try:
        dom = minidom.parseString(fileString)
        return dom.documentElement
    except ExpatError as inst:
        raise XMLError(_("FileString is an invalid XML: {}\n\nFileString: {}\n").format(
            str(inst), fileString))


def getAllNodes(node, tagPath):
    """retrieve all nodes that match a given tag path."""
    tags = tagPath.split('/')
    if len(tags) == 0:
        return []
    nodeList = [node]  # basis case
    for tag in tags:
        results = [getTagByName(x, tag) for x in nodeList]
        nodeList = []
        for x in results:
            nodeList.extend(x)
            pass  # emacs indentation error, keep it here
        if len(nodeList) == 0:
            return []
    return nodeList


def getNodeAttribute(node, attrname):
    """get named attribute from DOM node"""
    if not node.hasAttribute(attrname):
        return None
    return node.getAttribute(attrname)


def getAttributeList(node):
    return node.attributes


def setNodeAttribute(node, attrname, value):
    """get named attribute from DOM node"""
    return node.setAttribute(attrname, value)


def getChildElts(parent):
    """get only child elements"""
    return [x for x in parent.childNodes if x.nodeType == x.ELEMENT_NODE]


def getTagByName(parent, childName):
    return [x for x in parent.childNodes
            if x.nodeType == x.ELEMENT_NODE and x.tagName == childName]


def getNodeText(node, tagpath=""):
    """get the first child and expect it to be text!"""
    if tagpath != "":
        node = getNode(node, tagpath)
    try:
        child = node.childNodes[0]
    except IndexError:
        return None
    except AttributeError:  # no node by that name
        return None
    if child.nodeType == child.TEXT_NODE:
        # print('child_data=', child.data.strip())
        return child.data.strip()  # in any case, strip whitespaces...
    else:
        raise XMLError(
            _("getNodeText: Expected text node, got something else!"))


def getChildText(node_s, tagpath):
    """get the text of a child at the end of a tag path"""
    node = getNode(node_s, tagpath)
    if not node:
        return None
    return getNodeText(node)


def getNode(node, tagpath):
    """returns the *first* matching node for given tag path."""

    if tagpath == "":
        return node

    assert isinstance(tagpath, str)
    tags = tagpath.split('/')
    assert len(tags) > 0

    # iterative code to search for the path
    for tag in tags:
        currentNode = None
        for child in node.childNodes:
            if child.nodeType == node.ELEMENT_NODE and child.tagName == tag:
                currentNode = child
                break
        if not currentNode:
            return None
        else:
            node = currentNode
    return currentNode


def createTagPath(node, tags):
    """create new child at the end of a tag chain starting from node
    no matter what"""
    if len(tags) == 0:
        return node
    dom = node.ownerDocument
    for tag in tags:
        node = node.appendChild(dom.createElement(tag))
    return node


def addTagPath(node, tags, newnode=None):
    """add newnode at the end of a tag chain, smart one"""
    node = createTagPath(node, tags)
    if newnode:  # node to add specified
        node.appendChild(newnode)
    return node


def addNode(node, tagpath, newnode=None, branch=True):
    """add a new node at the end of the tree and returns it
    if newnode is given adds that node, too."""

    assert isinstance(tagpath, str)
    tags = []
    if tagpath != "":
        tags = tagpath.split('/')  # tag chain
    else:
        addTagPath(node, [], newnode)
        return node

    assert len(tags) > 0  # we want a chain

    # iterative code to search for the path

    if branch:
        rem = 1
    else:
        rem = 0

    while len(tags) > rem:
        tag = tags.pop(0)
        nodeList = getTagByName(node, tag)
        if len(nodeList) == 0:  # couldn't find
            tags.insert(0, tag)  # put it back in
            return addTagPath(node, tags, newnode)
        else:
            node = nodeList[len(nodeList) - 1]  # discard other matches
    else:
        # had only one tag..
        return addTagPath(node, tags, newnode)


def addText(node, tagPath, text, branch=True):
    newnode = node.ownerDocument.createTextNode(text)
    return addNode(node, tagPath, newnode, branch=branch)


def removeChild(node, doc):
    doc.removeChild(node)


def removeChildText(node):
    node.childNodes[0].nodeValue = ""


def removeAttribute(node):
    pass


def newNode(node, tag):
    return node.ownerDocument.createElement(tag)


def toString(node):
    return node.toxml()


def toPretty(node):
    return node.toprettyxml()

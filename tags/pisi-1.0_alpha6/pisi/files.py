# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Files module provides access to files.xml. files.xml is genarated
# during the build process of a package and used in installation.

# Authors:  Eray Ozkural <eray@uludag.org.tr>

from pisi.xmlext import *
from pisi.xmlfile import XmlFile
from pisi.util import Checks
import pisi.lockeddbshelve as shelve

class FileInfo:
    """FileInfo holds the information for a File node/tag in files.xml"""
    def __init__(self, _path = "", _type = "", _size = "", _hash = ""):
        self.path = _path
        self.type = _type
        self.size = _size
        self.hash = _hash

    def readnew(node):
        f = FileInfo()
        f.read(node)
        return f
    readnew = staticmethod(readnew)

    def read(self, node):
        self.path = getNodeText(getNode(node, "Path"))
        self.type = getNodeText(getNode(node, "Type"))
        self.size = getNodeText(getNode(node, "Size"))
        self.hash = getNodeText(getNode(node, "SHA1Sum"))

    def elt(self, dom):
        ## FIXME: looking for a better way to do it
        ## could apparently use helper functions to do this shorter
        elt = dom.createElement("File")
        pathElt = dom.createElement("Path")
        pathElt.appendChild(dom.createTextNode(self.path))
        typeElt = dom.createElement("Type")
        typeElt.appendChild(dom.createTextNode(self.type))
        sizeElt = dom.createElement("Size")
        sizeElt.appendChild(dom.createTextNode(self.size))
        hashElt = dom.createElement("SHA1Sum")
        hashElt.appendChild(dom.createTextNode(self.hash))
        elt.appendChild(pathElt)
        elt.appendChild(typeElt)
        elt.appendChild(sizeElt)
        elt.appendChild(hashElt)
        return elt

    def has_errors(self):
        err = Checks()
        err.has_tag(self.path, "File", "Path")
        err.has_tag(self.type, "File", "Type")
        err.has_tag(self.size, "File", "Size")
        err.has_tag(self.hash, "File", "SHA1Sum")
        return err.list
        
    def __str__(self):
        s = "%s, type: %s, size: %s, sha1sum: %s" %  (self.path, self.type,
                                                      self.size, self.hash)
        return s

class Files(XmlFile):
    
    def __init__(self):
        XmlFile.__init__(self, "Files")
        self.list = []

    def append(self, fileinfo):
        self.list.append(fileinfo)

    def read(self, filename):
        self.readxml(filename)

        fileElts = self.getAllNodes("File")
        self.list = [FileInfo.readnew(x) for x in fileElts]

    def write(self, filename):
        self.newDOM()
        document = self.dom.documentElement
        for x in self.list:
            document.appendChild(x.elt(self.dom))
        self.writexml(filename)

    def has_errors(self):
        err = Checks()
        for finfo in self.list:
            err.join(finfo.has_errors())
        return err.list

class FilesDB(shelve.LockedDBShelf):

    def __init__(self):
        shelve.LockedDBShelf.__init__(self, 'files')
        #self.files_dir = pisi.util.join_path(ctx.config.db_dir(), 'files')

    def add_files(self, pkg_name, files):
        for x in files.list:
            self[str(x.path)] = (pkg_name, x)

    def has_file(self, path):
        return self.has_key(str(path))

    def get_file(self, path):
        path = str(path)
        if not self.has_key(path):
            return None
        else:
            return self[path]

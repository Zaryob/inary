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

# Files module provides access to files.xml. files.xml is genarated
# during the build process of a package and used in installation.

# Authors:  Eray Ozkural <eray@uludag.org.tr>

import pisi.pxml.autoxml as autoxml
from pisi.util import Checks
import pisi.lockeddbshelve as shelve

class FileInfo:
    """File holds the information for a File node/tag in files.xml"""

    __metaclass__ = autoxml.autoxml

    t_Path = [ autoxml.String, autoxml.mandatory ]
    t_Type = [ autoxml.String, autoxml.mandatory ]
    t_Size = [ autoxml.Long, autoxml.optional ]
    t_Hash = [ autoxml.String, autoxml.optional, "SHA1Sum" ]

    def __str__(self):
        s = "%s, type: %s, size: %s, sha1sum: %s" %  (self.path, self.type,
                                                      self.size, self.hash)
        return s

class Files(autoxml.XmlFile):

    __metaclass__ = autoxml.autoxml

    tag = "Files"

    t_List = [ [FileInfo], autoxml.optional, "File"]

    def append(self, fileinfo):
        self.list.append(fileinfo)

class FilesDB(shelve.LockedDBShelf):

    def __init__(self):
        shelve.LockedDBShelf.__init__(self, 'files')

    def add_files(self, pkg_name, files):
        for x in files.list:
            self[str(x.path)] = (pkg_name, x)

    def remove_files(self, files):
        for x in files.list:
            self.delete(str(x.path))

    def has_file(self, path):
        return self.has_key(str(path))

    def get_file(self, path):
        path = str(path)
        if not self.has_key(path):
            return None
        else:
            return self[path]

    def get_files(self, glob):
        import fnmatch

        glob = str(glob)
        infos = []
        for key in self.keys():
            if fnmatch.fnmatch(key, glob):
                infos.append(self[key])

        return infos

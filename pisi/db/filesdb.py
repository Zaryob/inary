# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.db.lockeddbshelve as shelve

class Error(pisi.Error):
    pass

class FilesDB(shelve.LockedDBShelf):

    def __init__(self):
        shelve.LockedDBShelf.__init__(self, 'files')

    def add_files(self, pkg_name, files, txn = None):
        def proc(txn):
            for x in files.list:
                path = x.path
                del x.path # don't store redundant attribute in db
                self.put(path, (pkg_name, x), txn)
                x.path = path # store it back in
        self.txn_proc(proc, txn)

    def remove_files(self, files, txn = None):
        def proc(txn):
            for x in files.list:
                if self.has_key(x.path):
                    self.delete(x.path, txn)
        self.txn_proc(proc, txn)

    def has_file(self, path, txn = None):
        return self.has_key(str(path), txn)

    def get_file(self, path, txn = None):
        path = str(path)
        def proc(txn):
            if not self.has_key(path, txn):
                return None
            else:
                (name, fileinfo) = self.get(path, txn)
                fileinfo.path = path
                return (name, fileinfo)
        return self.txn_proc(proc, txn)

    def match_files(self, glob):
        # NB: avoid using, this reads the entire db
        import fnmatch
        glob = str(glob)
        infos = []
        for key in self.keys():
            if fnmatch.fnmatch(key, glob):

                # FIXME: Why should we assign path attribute manually
                # in fileinfo? This is also done in get_file(), seems
                # like a dirty workaround... - baris
                name = self[key][0]
                fileinfo = self[key][1]
                fileinfo.path = key
                infos.append((name, fileinfo))
        return infos

filesdb = None

def init():
    global filesdb
    if filesdb is not None:
        return filesdb

    filesdb = FilesDB()
    return filesdb

def finalize():
    global filesdb
    if filesdb is not None:
        filesdb.close()
        filesdb = None

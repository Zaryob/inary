# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Author: Eray Ozkural

from bsddb import db
import os, fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.lockeddbshelve as shelve
import pisi.context as ctx
import pisi.packagedb as packagedb
import pisi.util as util
from pisi.uri import URI
       
class Error(pisi.Error):
    pass

class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri

#class HttpRepo

#class FtpRepo

#class RemovableRepo


class RepoDB(object):
    """RepoDB maps repo ids to repository information"""

    def __init__(self):
        self.d = shelve.LockedDBShelf("repo")
        if not self.d.has_key("order"):
            self.d["order"] = []

    def init_dbs(self):
        # initialize package/source dbs
        for x in self.list():
            packagedb.add_db(x)

    def __del__(self):
        self.d.close()

    def repo_name(self, ix):
        l = self.list()
        return l[ix]

    def swap(self, x,y):
        l = self.d["order"]
        t = l[x]
        l[x] = l[y]
        l[y] = t
        self.d["order"] = l

    def has_repo(self, name):
        name = str(name)
        return self.d.has_key("repo-" + name)

    def get_repo(self, name):
        name = str(name)
        return self.d["repo-" + name]

    def add_repo(self, name, repo_info):
        if self.d.has_key("repo-" + name):
            raise Error(_('Repository %s already exists') % name)
        self.d["repo-" + name] = repo_info
        order = self.d["order"]
        order.append(name)
        self.d["order"] = order
        packagedb.add_db(name)

    def list(self):
        return self.d["order"]

    def clear(self):
        self.d.clear()

    def remove_repo(self, name):
        name = str(name)
        del self.d["repo-" + name]
        l = self.d["order"]
        l.remove(name)
        self.d["order"] = l
        

db = None

def init():
    global db
    if db:
        return db

    db = RepoDB()
    db.init_dbs()
    return db
    

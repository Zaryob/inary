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

import pisi.lockeddbshelve as shelve
import pisi.context as ctx
import pisi.packagedb as packagedb
import pisi.util as util
from pisi.uri import URI
       
class RepoDB(object):
    """RepoDB maps repo ids to repository information"""
    def __init__(self):
        self.d = shelve.LockedDBShelf("repo")

    def init_dbs(self):
        # initialize package/source dbs
        for x in self.d.keys():
            packagedb.add_db(x)

    def __del__(self):
        self.d.close()

    def has_repo(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_repo(self, name):
        name = str(name)
        return self.d[name]

    def add_repo(self, name, repo_info):
        self.d[name] = repo_info
        packagedb.add_db(name)

    def list(self):
        return self.d.keys()

    def clear(self):
        self.d.clear()

    def remove_repo(self, name):
        name = str(name)
        del self.d[name]

db = None

def init():
    global db
    if db:
        return db

    db = RepoDB()
    db.init_dbs()
    return db
    

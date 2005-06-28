# -*- coding: utf-8 -*-
# package database
# interface for update/query to local package repository
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

# we basically store everything in PackageInfo class
# yes, we are cheap

from bsddb.dbshelve import DBShelf
import os, fcntl

import util
from config import config
from bsddb import db

class PackageDB(DBShelf):

    def __init__(self):
        DBShelf.__init__(self)
        util.check_dir(config.db_dir())
        filename = os.path.join(config.db_dir(), 'package.bdb')
        #d.open(filename, dbname, filetype, flags, mode)
        flags = db.DB_CREATE
        mode = 0660
        filetype=db.DB_HASH
        dbname = None
        self.open( filename, dbname, filetype, flags, mode )
        self.fdummy = open(filename)
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def __del__(self):
        #fcntl.flock(self.fdummy, fcntl.LOCK_UN)
        self.fdummy.close()

    def has_package(self, name):
        name = str(name)
        return self.has_key(name)

    def get_package(self, name):
        name = str(name)
        return self[name]

    def add_package(self, package_info):
        name = str(package_info.name)
        self[name] = package_info

    def remove_package(self, name):
        name = str(name)
        del self[name]

packagedb = PackageDB()


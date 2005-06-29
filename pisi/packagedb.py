# -*- coding: utf-8 -*-
# package database
# interface for update/query to local package repository
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr

# we basically store everything in PackageInfo class
# yes, we are cheap

#from bsddb.dbshelve import DBShelf
import bsddb.dbshelve as shelve
import os, fcntl

import util
from config import config
from bsddb import db

class PackageDB(object):

    def __init__(self):
        util.check_dir(config.db_dir())
        filename = os.path.join(config.db_dir(), 'package.bdb')
        self.d = shelve.open(filename)
        self.fdummy = open(filename)
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def __del__(self):
        #fcntl.flock(self.fdummy, fcntl.LOCK_UN)
        self.fdummy.close()

    def has_package(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_package(self, name):
        name = str(name)
        return self.d[name]

    def add_package(self, package_info):
        name = str(package_info.name)
        self.d[name] = package_info

    def remove_package(self, name):
        name = str(name)
        del self.d[name]

packagedb = PackageDB()


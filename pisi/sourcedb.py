# -*- coding: utf-8 -*-
# package source database
# interface for update/query to local package repository
# Author:  Eray Ozkural <eray@uludag.org.tr>

# we basically store everything in sourceinfo class
# yes, we are cheap

import bsddb.dbshelve as shelve
import os, fcntl

import util
from config import config
from bsddb import db

class SourceDB(object):

    def __init__(self):
        util.check_dir(config.db_dir())
        self.filename = os.path.join(config.db_dir(), 'source.bdb')
        self.d = shelve.open(self.filename)
        self.fdummy = file(self.filename + '.lock', 'w')
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def __del__(self):
        #fcntl.flock(self.fdummy, fcntl.LOCK_UN)
        self.fdummy.close()
        #os.unlink(self.filename + '.lock')

    def has_source(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_source(self, name):
        name = str(name)
        return self.d[name]

    def add_source(self, source_info):
        assert source_info.verify()
        name = str(source_info.name)
        self.d[name] = source_info

    def remove_source(self, name):
        name = str(name)
        del self.d[name]

sourcedb = SourceDB()


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

# package source database
# interface for update/query to local package repository

# Author:  Eray Ozkural <eray@uludag.org.tr>

# we basically store everything in sourceinfo class
# yes, we are cheap

import bsddb.dbshelve as shelve
import os
import fcntl
from bsddb import db

import pisi.util as util
import pisi.context as ctx

class SourceDB(object):

    def __init__(self):
        util.check_dir(ctx.config.db_dir())
        self.filename = os.path.join(ctx.config.db_dir(), 'source.bdb')
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
        # FIXME: how can you make a negative assertion -gurer
        # and yes i'm not very clever :)
        # assert source_info.has_errors()
        name = str(source_info.name)
        self.d[name] = source_info

    def remove_source(self, name):
        name = str(name)
        del self.d[name]

sourcedb = None

def init():
    global sourcedb
    if sourcedb:
        return sourcedb

    sourcedb = SourceDB()
    return sourcedb
    

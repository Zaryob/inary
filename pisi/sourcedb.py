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
# Author:  Eray Ozkural <eray@uludag.org.tr>

"""
package source database
interface for update/query to local package repository
we basically store everything in sourceinfo class
yes, we are cheap
"""

import bsddb.dbshelve as shelve
import os
import fcntl
from bsddb import db

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.util as util
import pisi.context as ctx
import pisi.lockeddbshelve as shelve

class SourceDB(object):

    def __init__(self, id = 'repo'):
        self.d = shelve.LockedDBShelf('source-%s' % id)

    def close(self):
        self.d.close()

    def has_source(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_source(self, name):
        name = str(name)
        return self.d[name]

    def add_source(self, source_info):
        assert not source_info.errors()
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

def finalize():
    global sourcedb
    if sourcedb:
        sourcedb.close()
        sourcedb = None

sourcedbs = {}

def add_db(name):
    pisi.sourcedb.sourcedbs[name] = SourceDB('repo-' + name)

def get_db(name):
    return pisi.sourcedb.sourcedbs[name]

def remove_db(name):
    del pisi.sourcedb.sourcedbs[name]
    #FIXME: erase database file?
    
def has_package(name):
    repo = which_repo(name)
    if repo:# or thirdparty_packagedb.has_package(name) or inst_packagedb.has_package(name):
        return True
    return False

def which_repo(name):
    import pisi.repodb
    for repo in pisi.repodb.db.list():
        if get_db(repo).has_source(name):
            return repo
    return None

def get_package(name):
    repo = which_repo(name)
    if repo:
        return get_db(repo).get_source(name)
    if thirdparty_packagedb.has_source(name):
        return thirdparty_packagedb.get_source(name)
    if inst_packagedb.has_source(name):
        return inst_packagedb.get_source(name)
    raise Error(_('get_source: source %s not found') % name)

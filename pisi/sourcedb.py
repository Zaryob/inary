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
to handle multiple repositories, for sources, we 
store a set of repositories in which the source appears.
the actual guy to take is determined from the repo order.
"""

import os
import fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.util as util
import pisi.context as ctx
import pisi.lockeddbshelve as shelve
import pisi.repodb

class SourceDB(object):

    def __init__(self):
        self.d = shelve.LockedDBShelf('source')
        self.dpkgtosrc = shelve.LockedDBShelf('pkgtosrc')

    def close(self):
        self.d.close()
        self.dpkgtosrc.close()

    def list(self):
        list = []
        for (pkg, x) in self.d.items():
            list.append(pkg) # for some reason we couldn't return self.d.items()!! --exa
        return list

    def has_spec(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_spec(self, name):
        name = str(name)
        s = self.d[name]
        order = ctx.repodb.list()
        for repo in order:
            if s.has_key(repo):
                return (s[repo], repo) 
        return None

    def pkgtosrc(self, name):
        name = str(name)
        return self.dpkgtosrc[name]
        
    def add_spec(self, spec, repo, txn = None):
        assert not spec.errors()
        name = str(spec.source.name)
        repo = str(repo)
        def proc(txn):
            if not self.d.has_key(name):
                s = dict()
            else:
                s = self.d.get(name, txn)
            s[repo] = spec
            self.d.put(name, s, txn)
            for pkg in spec.packages:
                self.dpkgtosrc.put(pkg.name, name, txn)
        self.d.txn_proc(proc, txn)
        
    def remove_specfile(self, name, repo):
        name = str(name)
        repo = str(repo)
        def proc(txn):
        #assert self.has_source(name)
            s = self.d[name]
            s.remove(repo)
            if (len(s)==0):
                del self.d[name]
            else:
                self.d[name] = s
        self.d.txn_proc(proc, txn)

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

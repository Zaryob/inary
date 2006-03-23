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

import os
import fcntl
import types

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.util as util
import pisi.context as ctx
import pisi.lockeddbshelve as shelve

installed, thirdparty = range(2)

class Error(pisi.Error):
    pass

class NotfoundError(pisi.Error):
    pass
    
# the above are special databases to keep track of already installed stuff and 
# third party stuff not in any real repository

class ItemByRepoDB(object):

    def __init__(self, name):
        self.d = shelve.LockedDBShelf(name)
        #self.dbyrepo = shelve.LockedDBShelf(name + '-byrepo')

    def close(self):
        self.d.close()
        
    def clear(self, txn = None):
        self.d.clear(txn=txn)

    def txn_proc(self, proc, txn):
        self.d.txn_proc(proc, txn)

    def items(self):
        return self.d.items()
        
    def list(self, repo = None):
        if repo:
            return [ k for k,data in self.d.items() if data.has_key(self.repo_str(repo))]
        else:
            return [ pkg for pkg in self.d.keys() ]
        
    # TODO: carry this to repodb, really :/
    def order(self):
        import pisi.repodb
        order = [ 'repo-' + x for x in ctx.repodb.list() ] + ['trdparty', 'inst']
        return order

#    def list_repo(self, repo):
#        return self.dbyrepo[repo]

    def repo_str(self, repo):
        if repo==thirdparty:
            repo='trdparty'
        elif repo==installed:
            repo='inst'
        else:
            repo='repo-'+repo
        return repo
    
    def str_repo(self, str):
        if str.startswith('repo-'):
            return str[5:]
        elif str=='trdparty':
            return thirdparty
        elif str=='inst':
            return installed
        else:
            raise Error(_('Invalid repository string'))

    def has_key(self, name, repo = None, txn = None):
        name = str(name)
        haskey = self.d.has_key(name, txn)
        if not repo:
            return haskey
        else:
            return haskey and self.d.get(name, txn).has_key(repo)

    def get_item_repo(self, name, repo = None, txn = None):
        name = str(name)
        def proc(txn):
            if not self.d.has_key(name, txn=txn):
                raise NotfoundError(_('Key %s not found') % name)
            s = self.d.get(name, txn=txn)
            if not repo:
                for repostr in self.order():
                    if s.has_key(repostr):
                        return (s[repostr], self.str_repo(repostr))
            else:
                repostr = self.repo_str(repo)
                if s.has_key(repostr):
                    return (s[repostr], repo)
            return None
            
        return self.d.txn_proc(proc, txn)

    def get_item(self, name, repo = None, txn = None):
        x = self.get_item_repo(name, repo, txn)
        if x:
            item, repo = x
            # discard repo, not always needed
            return item
        else:
            return None

    def which_repo(self, name, repo = None, txn = None):
        x = self.get_item_repo(name, repo, txn)
        if x:
            item, repo = x
            return repo
        else:
            return None
        
    def add_item(self, name, obj, repo, txn = None):
        repostr = self.repo_str(repo)
        def proc(txn):
            if not self.d.has_key(name):
                s = dict()
            else:
                s = self.d.get(name, txn)
            s[ repostr ] = obj
            self.d.put(name, s, txn)
        self.d.txn_proc(proc, txn)
        
    def remove_item(self, name, repo, txn = None):
        name = str(name)
        repo = str(repo)
        def proc(txn):
            s = self.d.get(name, txn)
            repostr = self.repo_str(repo)
            if s.has_key(repostr):
                del s[repostr]
            if (len(s)==0):
                self.d.delete(name, txn)
            else:
                self.d.put(name, s, txn)
        self.d.txn_proc(proc, txn)

    def remove_repo(self, repo, txn = None):
        def proc(txn):
            repostr = self.repo_str(repo)
            for (key, s) in self.d.items():
                if s.has_key(repostr):
                    del s[repostr]
                self.d.put(repo, s, txn)
        self.d.txn_proc(proc, txn)

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

# package database
# interface for update/query to local package repository

# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>

# we basically store everything in PackageInfo class
# yes, we are cheap

import os, fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.util as util
import pisi.context as ctx
import pisi.lockeddbshelve as shelve

class Error(pisi.Error):
    pass

class PackageDB(object):
    """PackageDB class provides an interface to the package database 
    using shelf objects"""
    def __init__(self, id):
        self.d = shelve.LockedDBShelf('package-%s' % id )
        self.dr = shelve.LockedDBShelf('revdep-%s' % id )

    def close(self):
        self.d.close()
        self.dr.close()

    def has_package(self, name, txn = None):
        name = str(name)
        return self.d.has_key(name, txn)

    def get_package(self, name):
        name = str(name)
        return self.d[name]

    def get_rev_deps(self, name):
        name = str(name)
        if self.dr.has_key(name):
            return self.dr[name]
        else:
            return []

    def list_packages(self):
        list = []
        for (pkg, x) in self.d.items():
            list.append(pkg)
        return list

    #TODO: list_upgrades?

    def add_package(self, package_info, txn = None):
        name = str(package_info.name)
        
        def proc(txn):
            self.d.put(name, package_info, txn)
            for dep in package_info.runtimeDependencies():
                dep_name = str(dep.package)
                if self.dr.has_key(dep_name, txn):
                    revdep = self.dr.get(dep_name, txn)
                    revdep.append( (name, dep) )
                    self.dr.put(dep_name, revdep, txn)
                else:
                    self.dr.put(dep_name, [ (name, dep) ], txn)
            # add component
            ctx.componentdb.add_package(package_info.partOf, package_info.name, txn)
            # index summary and description
            for (lang, doc) in package_info.summary.iteritems():
                if lang in ['en', 'tr']:
                    pisi.search.add_doc('summary', lang, package_info.name, doc, txn)
            for (lang, doc) in package_info.description.iteritems():
                if lang in ['en', 'tr']:
                    pisi.search.add_doc('description', lang, package_info.name, doc, txn)

        self.d.txn_proc(proc, txn)

    def clear(self):
        self.d.clear()

    def remove_package(self, name, txn = None):
        name = str(name)
        def proc(txn):
            package_info = self.d.get(name, txn)
            self.d.delete(name, txn)
            #FIXME: what's happening to dr?
            ctx.componentdb.remove_package(package_info.partOf, package_info.name, txn)
        self.d.txn_proc(proc, txn)

packagedbs = {}

def add_db(name):
    pisi.packagedb.packagedbs[name] = PackageDB('repo-' + name)

def get_db(name):
    return pisi.packagedb.packagedbs[name]

def remove_db(name):
    del pisi.packagedb.packagedbs[name]
    #FIXME: erase database file?
    
def has_package(name, txn = None):
    def proc(txn):
        repo = which_repo(name)
        if repo or thirdparty_packagedb.has_package(name, txn) or inst_packagedb.has_package(name, txn):
            return True
        return False
    return ctx.txn_proc(proc, txn)

def which_repo(name, txn = None):
    import pisi.repodb
    def proc(txn):
        for repo in pisi.repodb.db.list():
            if get_db(repo).has_package(name, txn):
                return repo
        return None
    return ctx.txn_proc(proc, txn)

def get_package(name):
    repo = which_repo(name)
    if repo:
        return get_db(repo).get_package(name)
    if thirdparty_packagedb.has_package(name):
        return thirdparty_packagedb.get_package(name)
    if inst_packagedb.has_package(name):
        return inst_packagedb.get_package(name)
    raise Error(_('get_package: package %s not found') % name)

def get_rev_deps(name):
    repo = which_repo(name)
    if repo:
        return get_db(repo).get_rev_deps(name)
    if thirdparty_packagedb.has_package(name):
        return thirdparty_packagedb.get_rev_deps(name)    
    if inst_packagedb.has_package(name):
        return inst_packagedb.get_rev_deps(name)

    return []

def remove_package(name, txn = None):
    # remove the guy from the tracking databases
    inst_packagedb.remove_package(name, txn)
    if thirdparty_packagedb.has_package(name, txn):
        thirdparty_packagedb.remove_package(name, txn)

# tracking databases for non-repository information

thirdparty_packagedb = inst_packagedb = None

def init_db():
    global thirdparty_packagedb
    global inst_packagedb

    if not thirdparty_packagedb:
        thirdparty_packagedb = PackageDB('thirdparty')
    if not pisi.packagedb.inst_packagedb:
        inst_packagedb = PackageDB('installed')

def finalize_db():
    global thirdparty_packagedb
    global inst_packagedb
    global packagedbs

    if thirdparty_packagedb:
        thirdparty_packagedb.close()
        thirdparty_packagedb = None

    if inst_packagedb:
        inst_packagedb.close()
        inst_packagedb = None
    
    packagedbs.clear()

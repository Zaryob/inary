# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""package database
interface for update/query to local package repository

we basically store everything in PackageInfo class
yes, we are cheap
"""

import os
import fcntl
import types

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.util as util
import pisi.context as ctx
import pisi.db.itembyrepodb as itembyrepodb


class Error(pisi.Error):
    pass

class NotfoundError(pisi.Error):
    def __init__(self, pkg):
        pisi.Error.__init__("Package %s not found" % pkg)
        self.pkg = pkg

class PackageDB(object):
    """PackageDB class provides an interface to the package database
    using shelf objects"""

    def __init__(self):
        self.d = itembyrepodb.ItemByRepoDB('package')
        self.dbHistory = itembyrepodb.ItemByRepoDB('package_history')
        self.dr = itembyrepodb.ItemByRepoDB('revdep')

    def close(self):
        self.d.close()
        self.dbHistory.close()
        self.dr.close()

    def destroy(self):
        self.d.destroy()
        self.dbHistory.destroy()
        self.dr.destroy()
        
    def clear(self, txn = None):
        self.d.clear()
        self.dbHistory.clear()
        self.dr.clear()

    def has_package(self, name, repo=None, txn = None):
        return self.d.has_key(name, repo, txn=txn)

    def get_package(self, name, repo=None, txn = None):
        try:
            return self.d.get_item(name, repo, txn=txn)
        except pisi.db.itembyrepodb.NotfoundError, e:
            raise Error(_('Package %s not found') % name)

    def get_history(self, name, repo=None, txn = None):
        try:
            return self.dbHistory.get_item(name, repo, txn=txn)
        except pisi.db.itembyrepodb.NotfoundError, e:
            raise Error(_('History for Package %s not found') % name)

    def get_package_repo(self, name, repo=None, txn = None):
        return self.d.get_item_repo(name, repo, txn=txn)

    def which_repo(self, name, txn = None):
        return self.d.which_repo(name, txn=txn)

    def get_rev_deps(self, name, repo = None, txn = None):
        if self.dr.has_key(name, repo, txn=txn):
            return self.dr.get_item(name, repo, txn=txn)
        else:
            return []

    def get_deps(self, name, repo = None, txn = None):
        if self.d.has_key(name, repo, txn=txn):
            pinfo =  self.d.get_item(name, repo, txn=txn)
            return pinfo.packageDependencies
        else:
            return []

    def list_packages(self, repo=None):
        return self.d.list(repo)

    def add_package(self, package_info, repo, txn = None):
        name = str(package_info.name)

        def proc(txn):
            self.dbHistory.add_item(name, package_info.history, repo, txn)
            package_info.history = None
            self.d.add_item(name, package_info, repo, txn)
            for dep in package_info.runtimeDependencies():
                dep_name = str(dep.package)
                if self.dr.has_key(dep_name, repo, txn):
                    revdep = self.dr.get_item(dep_name, repo, txn)
                    revdep = filter(lambda (n,d):n!=name, revdep)
                    revdep.append( (name, dep) )
                    self.dr.add_item(dep_name, revdep, repo, txn)
                else:
                    self.dr.add_item(dep_name, [ (name, dep) ], repo, txn)
            # add component
            ctx.componentdb.add_package(package_info.partOf, package_info.name, repo, txn)
        ctx.txn_proc(proc, txn)

    def remove_package(self, name, repo = None, txn = None):
        name = str(name)
        def proc(txn):
            package_info = self.d.get_item(name, repo, txn=txn)
            self.d.remove_item(name, repo, txn=txn)
            self.dbHistory.remove_item(name, repo, txn=txn)
            for dep in package_info.runtimeDependencies():
                dep_name = str(dep.package)
                if self.dr.has_key(dep_name, repo, txn):
                    revdep = self.dr.get_item(dep_name, repo, txn)
                    revdep = filter(lambda (n,d):n!=name, revdep)
                    if revdep:
                        self.dr.add_item(dep_name, revdep, repo, txn)
                    else:
                        # Bug 3558: removal of revdep list of a package from revdepdb
                        # should only be done by the list members (dep. packages), not
                        # the package itself. So if a package is removed, it is removed
                        # from packagedb but its revdepdb part may still exist, until
                        # all the list members are removed.
                        self.dr.remove_item(dep_name, repo, txn=txn)

            # remove from component
            ctx.componentdb.remove_package(package_info.partOf, package_info.name, repo, txn)

        self.d.txn_proc(proc, txn)

    def remove_repo(self, repo, txn = None):
        def proc(txn):
            self.d.remove_repo(repo, txn=txn)
            self.dr.remove_repo(repo, txn=txn)
        self.d.txn_proc(proc, txn)

pkgdb = None

def remove_tracking_package(name, txn = None):
    # remove the guy from the tracking databases
    if pkgdb.has_package(name, itembyrepodb.installed, txn=txn):
        pkgdb.remove_package(name, itembyrepodb.installed, txn=txn)
    if pkgdb.has_package(name, itembyrepodb.thirdparty, txn=txn):
        pkgdb.remove_package(name, itembyrepodb.thirdparty, txn=txn)

def init_db():
    global pkgdb
    pkgdb = PackageDB()
    return pkgdb

def finalize_db():
    global pkgdb
    if pkgdb:
        pkgdb.close()

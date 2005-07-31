# -*- coding: utf-8 -*-
# package database
# interface for update/query to local package repository
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>

# we basically store everything in PackageInfo class
# yes, we are cheap

#from bsddb.dbshelve import DBShelf
import bsddb.dbshelve as shelve
import os, fcntl
import atexit

import util
from config import config
from bsddb import db

class PackageDBError(Exception):
    pass

class PackageDB(object):
    """PackageDB class provides an interface to the package database with
    a delegated dbshelve object"""
    def __init__(self, id):
        util.check_dir(config.db_dir())
        self.fname = os.path.join(config.db_dir(), 'package-%s.bdb' % id )
        self.d = shelve.open(self.fname)
        self.fname2 = os.path.join(config.db_dir(), 'revdep-%s.bdb'  % id )
        self.dr = shelve.open(self.fname2)
        
        self.lockfile = self.fname + '.lock'
 
        self.fdummy = file(self.lockfile, 'w')
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def has_package(self, name):
        name = str(name)
        return self.d.has_key(name)

    def get_package(self, name):
        name = str(name)
        return self.d[name]

    def get_rev_deps(self, name):
        name = str(name)
        if self.dr.has_key(name):
            return self.dr[name]
        else:
            return []

    def add_package(self, package_info):
        name = str(package_info.name)
        self.d[name] = package_info
        for dep in package_info.runtimeDeps:
            dep_name = str(dep.package)
            if self.dr.has_key(dep_name):
                self.dr[dep_name].append( (name, dep) )
            else:
                self.dr[dep_name] = [ (name, dep) ]

    def clear(self):
        self.d.clear()

    def remove_package(self, name):
        name = str(name)
        del self.d[name]


packagedbs = {}

def add_db(name):
    packagedbs[name] = PackageDB('repo-' + name)

def get_db(name):
    return packagedbs[name]

def remove_db(name):
    del packagedbs[name]
    #erase database file

def has_package(name):
    repo = which_repo(name)
    if repo or thirdparty_packagedb.has_package(name):
        return True
    return False

def which_repo(name):
    for repo in packagedbs.keys():
        if get_db(repo).has_package(name):
            return repo
    return None

def get_package(name):
    repo = which_repo(name)
    if repo:
        return get_db(repo).get_package(name)
    if thirdparty_packagedb.has_package(name):
        return thirdparty_packagedb.get_package(name)
    raise PackageDBError, 'get_package: package %s not found' % name

def get_rev_deps(name):
    repo = which_repo(name)
    if repo:
        return get_db(repo).get_rev_deps(name)
    if thirdparty_packagedb.has_package(name):
        return thirdparty_packagedb.get_rev_deps(name)    

inst_packagedb = PackageDB('installed')
thirdparty_packagedb = PackageDB('thirdparty')

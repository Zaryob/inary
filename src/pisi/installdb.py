# -*- coding: utf-8 -*-
# installation database
# maintainer: eray and caglar

from context import Context
import util
import bsddb.dbshelve as shelve

util.check_dir(Context.db_dir())
d = shelve.open(Context.db_dir() + '/install.bdb')
files_dir = Context.archives_dir() + "/files"

class InstallDBError(Exception):
    pass

def files_name(name, version, release):
    return files + '/' + name + '-' + version + '-' + release

def is_recorded(name, version, release):
    key = (name, version, release)
    return d.has_key(key)

def is_installed(name, version, release):
    key = (name, version, release)
    return is_recorded(key) and d[key]=='i'

def install(name, version, release, files_xml):
    key = (name, version, release)
    if isInstalled(key):
        raise InstallDBError("already installed")
    d[key] = 'i'
    util.copy_file(files_xml, files_name(name, version, release))
                   
def remove(name, version, release):
    key = (name, version, release)
    d[key] = 'r'

def purge(name, version, release):
    util.remove_file(files_name(name, version, release))
    del d[key]



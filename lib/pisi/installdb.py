# -*- coding: utf-8 -*-
# installation database
# maintainer: eray and caglar

import os
import bsddb.dbshelve as shelve

from context import ctx
import util

util.check_dir(ctx.db_dir())
d = shelve.open(ctx.db_dir() + '/install.bdb')
files_dir = ctx.archives_dir() + "/files"

class InstallDBError(Exception):
    pass

def files_name(name, version, release):
    return files_dir + '/' + name + '-' + version + '-' + release

def files(n, v, r):
    return file(files_name(n,v,r))

def is_recorded(name, version, release):
    key = name + version + release
    return d.has_key(key)

def is_installed(name, version, release):
    key = name + version + release
    return is_recorded(name,version,release) and d[key]=='i'

def is_removed(name, version, release):
    key = name + version + release
    return is_recorded(name,version,release) and d[key]=='r'

def install(name, version, release, files_xml):
    key = name + version + release
    if is_installed(name, version, release):
        raise InstallDBError("already installed")
    d[key] = 'i'
    util.copy_file(files_xml, files_name(name, version, release))
                   
def remove(name, version, release):
    key = name + version + release
    d[key] = 'r'

def purge(name, version, release):
    os.unlink(files_name(name, version, release))
    key = name + version + release
    del d[key]



# -*- coding: utf-8 -*-
# installation database
# maintainer: eray and caglar

import os
import bsddb.dbshelve as shelve

from context import ctx
import util

util.check_dir(ctx.db_dir())
d = shelve.open(ctx.db_dir() + '/install.bdb')
print 'installdb:', ctx.db_dir() + '/install.bdb'
files_dir = ctx.archives_dir() + "/files"

class InstallDBError(Exception):
    pass

def files_name(pkg, version, release):
    return files_dir + '/' + pkg + '-' + version + '-' + release + '.xml'

def files(pkg):
    (status, version, release) = d[pkg]
    return file(files_name(pkg,version,release))

def is_recorded(pkg):
    return d.has_key(pkg)

def is_installed(pkg):
    if is_recorded(pkg):
        (status, version, release) = d[pkg]
        return status=='i'
    else:
        return False

def get_version(pkg):
    (status, version, release) = d[pkg]
    return (version, release)

def is_removed(pkg):
    if is_recorded(pkg):
        (status, version, release) = d[pkg]
        return status=='r'
    else:
        return False

def install(pkg, version, release, files_xml):
    """install package with specific version and release"""
    if is_installed(pkg):
        raise InstallDBError("already installed")
    d[pkg] = ('i', version, release)
    util.copy_file(files_xml, files_name(pkg, version, release))
                   
def remove(pkg):
    (status, version, release) = d[pkg]
    d[pkg] = ('r', version, release)

def purge(pkg):
    if d.has_key(pkg):
        (status, version, release) = d[pkg]
	f = files_name(pkg, version, release)
	if util.check_file(f):
	    os.unlink(f)
	del d[pkg]



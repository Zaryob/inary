# -*- coding: utf-8 -*-
# installation database
# Author:  Eray Ozkural <eray@uludag.org.tr>


import os
import bsddb.dbshelve as shelve

from config import config
import util

util.check_dir(config.db_dir())
d = shelve.open(config.db_dir() + '/install.bdb')
files_dir = config.db_dir() + "/files"

class InstallDBError(Exception):
    pass

def files_name(pkg, version, release):
    return str(files_dir + '/' + pkg + '-' + version + '-' + release + '.xml')

def files(pkg):
    pkg = str(pkg)
    (status, version, release) = d[pkg]
    return file(files_name(pkg,version,release))

def is_recorded(pkg):
    pkg = str(pkg)
    return d.has_key(pkg)

def is_installed(pkg):
    pkg = str(pkg)
    if is_recorded(pkg):
        (status, version, release) = d[pkg]
        return status=='i'
    else:
        return False

def get_version(pkg):
    pkg = str(pkg)
    (status, version, release) = d[pkg]
    return (version, release)

def is_removed(pkg):
    pkg = str(pkg)
    if is_recorded(pkg):
        (status, version, release) = d[pkg]
        return status=='r'
    else:
        return False

def install(pkg, version, release, files_xml):
    """install package with specific version and release"""
    pkg = str(pkg)
    if is_installed(pkg):
        raise InstallDBError("already installed")
    d[pkg] = ('i', version, release)
    util.copy_file(files_xml, files_name(pkg, version, release))
                   
def remove(pkg):
    pkg = str(pkg)
    (status, version, release) = d[pkg]
    d[pkg] = ('r', version, release)

def purge(pkg):
    pkg = str(pkg)
    if d.has_key(pkg):
        (status, version, release) = d[pkg]
        f = files_name(pkg, version, release)
        if util.check_file(f):
            os.unlink(f)
        del d[pkg]

# -*- coding: utf-8 -*-
# installation database
# maintainer: eray and caglar

import config
import shelve
import util

util.check_dir( config.db_dir() )

d = shelve.open( config.db_dir() + '/install.dbm')

files_dir = config.archives_dir() + "/files"

class InstallDBError(Exception):
    pass

def files_name(name, version, release):
    return files + '/' + name + '-' + version + '-' + release

def is_recorded(name, version, release):
    key = (name, version, release)
    return d.has_key( key )

def is_installed(name, version, release):
    key = (name, version, release)
    return is_recorded(key) and d[key]=='i'

def install( name, version, release, files_xml):
    key = (name, version, release)
    if isInstalled(key):
        raise InstallDBError("already installed")
    d[key] = 'i'
    util.copy_file(files_xml, files_name( name, version, release) )
                   
def remove( name, version, release):
    key = (name, version, release)
    d[key] = 'r'

def purge( name, version, release):
    d.delete(key)
    util.remove_file( files_name( name, version, release) )



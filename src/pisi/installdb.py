# -*- coding: utf-8 -*-
# installation database

import shelve

d = shelve.open( db_dir + '/install.dbm')

class InstallDBError(Exception):
    pass



def isRecorded(name, version, release):
    return d.has_key( (name, version, release) )

def isInstalled(name, version, release):
    return d.has_key( (name, version, release) )

def install( name, version, release, state):
    if isInstalled(name,version,release):
        raise InstallDBError("already installed")
    d[ (name,version,release) ] = state
    
def remove( name, version, release):
    if 

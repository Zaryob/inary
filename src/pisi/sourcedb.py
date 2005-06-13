# -*- coding: utf-8 -*-
# package source database
# interface for update/query to local package repository
# maintainer: eray and caglar

# we basically store everything in sourceinfo class (?)
# yes, we are cheap

import bsddb.dbshelve as shelve

util.check_dir( config.db_dir() )
d = shelve.open( config.db_dir() + '/source.bdb')

def add_source( name, source_info ):
    d[name] = source_info

def remove_source(name):
    del d[name]

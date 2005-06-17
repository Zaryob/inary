# -*- coding: utf-8 -*-
# package database
# interface for update/query to local package repository
# maintainer: eray and caglar

# we basically store everything in PackageInfo class
# yes, we are cheap

import bsddb.dbshelve as shelve

import util
from context import ctx

util.check_dir(ctx.db_dir())
d = shelve.open(ctx.db_dir() + '/package.bdb')

def has_package(name):
    return d.has_key(name)

def get_package(name):
    return d[name]

def add_package(name, package_info):
    d[name] = package_info

def remove_package(name):
    del d[name]


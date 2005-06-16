# -*- coding: utf-8 -*-
# package database
# interface for update/query to local package repository
# maintainer: eray and caglar

# we basically store everything in PackageInfo class
# yes, we are cheap

import bsddb.dbshelve as shelve

import util
import config

util.check_dir(config.db_dir())
d = shelve.open(config.db_dir() + '/package.bdb')

def add_package(name, package_info):
    d[name] = package_info

def remove_package(name):
    del d[name]


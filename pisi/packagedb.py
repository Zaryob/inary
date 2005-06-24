# -*- coding: utf-8 -*-
# package database
# interface for update/query to local package repository
# maintainer: eray and caglar

# we basically store everything in PackageInfo class
# yes, we are cheap

import bsddb.dbshelve as shelve
import os

import util
from config import config

util.check_dir(config.db_dir())
d = shelve.open( os.path.join(config.db_dir(), 'package.bdb') )

def clear():
    d.clear()

def has_package(name):
    name = str(name)
    return d.has_key(name)

def get_package(name):
    name = str(name)
    return d[name]

def add_package(package_info):
    name = str(package_info.name)
    d[name] = package_info

def remove_package(name):
    name = str(name)
    del d[name]

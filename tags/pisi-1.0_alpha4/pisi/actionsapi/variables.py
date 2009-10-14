#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Standard Python Modules
from os import getenv, environ

# Pisi-Core Modules
import pisi.context as ctx

# Set individual information, that are generally needed for ActionsAPI

def exportFlags():
    '''General flags used in actions API.'''

    # Build systems depend on these environment variables. That is why
    # we export them instead of using as (instance) variables.
    values = ctx.config.values
    environ['HOST'] =  values.build.host
    environ['CFLAGS'] = values.build.cflags
    environ['CXXFLAGS'] = values.build.cxxflags
    environ['LDFLAGS'] = values.build.ldflags

class Env(object):
    '''General environment variables used in actions API'''
    def __init__(self):

        exportFlags()

        self.__vars = {
            'pkg_dir': 'PKG_DIR',
            'work_dir': 'WORK_DIR',
            'install_dir': 'INSTALL_DIR',
            'src_name': 'SRC_NAME',
            'src_version': 'SRC_VERSION',
            'src_release': 'SRC_RELEASE',
            'host': 'HOST',
            'cflags': 'CFLAGS',
            'cxxflags': 'CXXFLAGS',
            'ldflags': 'LDFLAGS'
        }

    def __getattr__(self, attr):

        # Using environment variables is somewhat tricky. Each time
        # you need them you need to check for their value.
        if self.__vars.has_key(attr):
            return getenv(self.__vars[attr])
        else:
            return None

class Dirs:
    '''General directories used in actions API.'''
    # TODO: Eventually we should consider getting these from a/the
    # configuration file
    doc = 'usr/share/doc'
    sbin = 'usr/sbin'
    man = 'usr/share/man'
    info = 'usr/share/info'
    data = 'usr/share'
    conf = 'etc'
    localstate = 'var/lib'
    defaultprefix = 'usr'

    #FIXME: Get these from config or somewhere else!
    kde = '/usr/kde/3.4'
    qt = '/usr/qt/3'

def initVariables():
    ctx.env = Env()
    ctx.dirs = Dirs()
    return ctx

glb = initVariables()

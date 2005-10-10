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

# Standart Python Modules
import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# PISI Modules
import pisi.actionsapi
import pisi.context as ctx

# ActionsAPI Modules
from variables import glb

class BinutilsError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

# Globals                                
env = glb.env
dirs = glb.dirs

def curDIR():
    '''returns current work directory's path'''
    return os.getcwd()

def curKERNEL():
    '''returns currently running kernel's version'''
    versionString = file("/proc/version").readline()
    return versionString.split()[2]

def ENV(environ):
    '''returns any given environ variable'''
    return os.environ[environ];

# PİSİ Related Functions

def pkgDIR():
    '''returns the path of binary packages'''
    '''Default: /var/cache/pisi/packages''' 
    return env.pkg_dir

def workDIR():
    return env.work_dir

def installDIR():
    '''returns the path of binary packages'''
    return env.install_dir

# PSPEC Related Functions

def srcNAME():
    return env.src_name

def srcVERSION():
    return env.src_version

def srcRELEASE():
    return env.src_release

def srcTAG():
    return env.src_name + '-' + env.src_version + '-' + env.src_release

def srcDIR():
    return env.src_name + '-' + env.src_version

# Build Related Functions
        
def HOST():
    return env.host

def CHOST():
    # FIXME: Currently it behave same as HOST,
    # but will be used for cross-compiling when PİSİ ready...           
    return env.host

def CFLAGS():
    return env.cflags

def CXXFLAGS():
    return env.cxxflags

def LDFLAGS():
    return env.ldflags

# Directory Related Functions

def docDIR():
    return dirs.doc

def sbinDIR():
    return dirs.sbin

def infoDIR():
    return dirs.info

def manDIR():
    return dirs.man

def dataDIR():
    return dirs.data

def confDIR():
    return dirs.conf

def localstateDIR():
    return dirs.localstate

def defaultprefixDIR():
    return dirs.defaultprefix

def kdeDIR():
    # FIXME: Get followings from env.d or somewhere else
    return dirs.kde

def qtDIR():
    # FIXME: Get followings from env.d or somewhere else
    return dirs.qt

def qtLIBDIR():
    # FIXME: Get followings from env.d or somewhere else
    return '%s/lib/' % qtDIR()

# Binutils Variables

def existBinary(bin):
    # determine if path has binary
    path = os.environ['PATH'].split(':')
    for directory in path:
        if os.path.exists(os.path.join(directory, bin)):
            return True
    return False

def getBinutilsInfo(util):
    cross_build_name = '%s-%s' % (HOST(), util)
    if not existBinary(cross_build_name):
        if not existBinary(util):
            raise BinutilsError(_('Util %s cannot be found') % util)
        else:
            ctx.ui.debug(_('Warning: %s does not exist, using plain name %s') \
                     % (cross_build_name, util))
            return util
    else:
        return cross_build_name

def AR():
    return getBinutilsInfo('ar')

def AS():
    return getBinutilsInfo('as')

def CC():
    return getBinutilsInfo('gcc')

def CXX():
    return getBinutilsInfo('g++')

def LD():
    return getBinutilsInfo('ld')

def NM():
    return getBinutilsInfo('nm')

def RANLIB():
    return getBinutilsInfo('ranlib')

def F77():
    return getBinutilsInfo('f77')

def GCJ():
    return getBinutilsInfo('gcj')

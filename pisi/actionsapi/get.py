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

# PISI Modules
import pisi.actionsapi
import pisi.context as ctx

# ActionsAPI Modules
from variables import glb

class BinutilsError(pisi.actionsapi.Error):
    pass

env = glb.env
dirs = glb.dirs

def curDIR():
    return os.getcwd()

def ENV(environ):
    return os.environ[environ];

# variables.Env 

def pkgDIR():
    return env.pkg_dir

def workDIR():
    return env.work_dir

def installDIR():
    return env.install_dir

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
        
def HOST():
    return env.host

def CFLAGS():
    return env.cflags

def CXXFLAGS():
    return env.cxxflags

def LDFLAGS():
    return env.ldflags

# variables.Dirs

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
    return dirs.kde

def qtDIR():
    return dirs.qt

def qtLIBDIR():
    return '%s/lib/' % qtDIR()

# Binutils Variables

def exists_binary(bin):
    # determine if path has binary
    path = os.environ['PATH'].split(':')
    for directory in path:
        if os.path.exists(os.path.join(directory, bin) ):
            return True
    return False

def getBinutilsInfo(util):
    cross_build_name = '%s-%s' % (HOST(), util)
    if not exists_binary(cross_build_name):
        if not exists_binary(util):
            raise BinutilsError('util %s cannot be found' % util)
        else:
            ctx.ui.debug('Warning: %s does not exist, using plain name %s' \
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

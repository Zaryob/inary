# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Standart Python Modules
import os
import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# PiSi Modules
import pisi.actionsapi
import pisi.util
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi.variables

class BinutilsError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

# Globals
env = pisi.actionsapi.variables.glb.env
dirs = pisi.actionsapi.variables.glb.dirs
config = pisi.actionsapi.variables.glb.config
generals = pisi.actionsapi.variables.glb.generals

def curDIR():
    '''returns current work directory's path'''
    return os.getcwd()

def curKERNEL():
    '''returns currently running kernel's version'''
    return os.uname()[2]

def curPYTHON():
    ''' returns currently used python's version'''
    (a, b, c, x, y) = sys.version_info
    return 'python%s.%s' % (a, b)

def curPERL():
    ''' returns currently used perl's version'''
    return os.path.realpath('/usr/bin/perl').split('perl')[1]

def ENV(environ):
    '''returns any given environ variable'''
    try:
        return os.environ[environ];
    except KeyError:
        return None

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

# Pardus Related Functions

def lsbINFO():
    """Returns a dictionary filled through /etc/lsb-release."""
    return dict([(l.split("=")[0], l.split("=")[1].strip("'\"")) \
                for l in open("/etc/lsb-release", "r").read().strip().split("\n") if "=" in l])

# PSPEC Related Functions

def srcNAME():
    return env.src_name

def srcVERSION():
    return env.src_version

def srcRELEASE():
    return env.src_release

def srcTAG():
    return '%s-%s-%s' % (env.src_name, env.src_version, env.src_release)

def srcDIR():
    return '%s-%s' % (env.src_name, env.src_version)

# Build Related Functions

def ARCH():
    return generals.architecture

def HOST():
    return env.host

def CHOST():
    # FIXME: Currently it behave same as HOST,
    # but will be used for cross-compiling when pisi ready...
    return env.host

def CFLAGS():
    return env.cflags

def CXXFLAGS():
    return env.cxxflags

def LDFLAGS():
    return env.ldflags

def makeJOBS():
    return env.jobs

def buildTYPE():
    '''returns the current build type'''
    return env.build_type

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

def libexecDIR():
    return dirs.libexec

def defaultprefixDIR():
    return dirs.defaultprefix

def kdeDIR():
    return dirs.kde

def qtDIR():
    return dirs.qt

# Binutils Variables

def AR():
    return config.values.build.ar

def AS():
    return config.values.build.assembler

def CC():
    return config.values.build.cc

def CXX():
    return config.values.build.cxx

def LD():
    return config.values.build.ld

def NM():
    return config.values.build.nm

def RANLIB():
    return config.values.build.ranlib

def F77():
    return config.values.build.f77

def GCJ():
    return config.values.build.gcj

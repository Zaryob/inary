# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Standard Python Modules
import os

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# Inary Modules
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi
import inary.actionsapi.get as get
from inary.actionsapi.shelltools import system
from inary.actionsapi.shelltools import can_access_file
from inary.actionsapi.shelltools import unlink
from inary.actionsapi.libtools import gnuconfig_update
from inary.actionsapi.shelltools import isDirectory
from inary.actionsapi.shelltools import ls
from inary.actionsapi.inarytools import dosed
from inary.actionsapi.inarytools import removeDir

class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)
        if can_access_file('config.log'):
            ctx.ui.error(_('Please attach the config.log to your bug report:\n{}/config.log').format(os.getcwd()))

class MakeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def configure(parameters = ''):
    '''configure source with given parameters = "--with-nls --with-libusb --with-something-usefull"'''

    if can_access_file('configure'):
        gnuconfig_update()

        prefix = get.emul32prefixDIR() if get.buildTYPE() == "emul32" else get.defaultprefixDIR()
        args = './configure \
                --prefix=/{0} \
                --build={1.HOST()} \
                --mandir=/{1.manDIR()} \
                --infodir=/{1.infoDIR()} \
                --datadir=/{1.dataDIR()} \
                --sysconfdir=/{1.confDIR()} \
                --localstatedir=/{1.localstateDIR()} \
                --libexecdir=/{1.libexecDIR()} \
                {2}{3}'.format(prefix, \
                         get,
                         "--libdir=/usr/lib32 " if get.buildTYPE() == "emul32" else "",
                         parameters)

        if system(args):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(_('No configure script found.'))

def rawConfigure(parameters = ''):
    '''configure source with given parameters = "--prefix=/usr --libdir=/usr/lib --with-nls"'''
    if can_access_file('configure'):
        gnuconfig_update()

        if system('./configure {}'.format(parameters)):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(_('No configure script found.'))

def compile(parameters = ''):
    system('{0} {1} {2}'.format(get.CC(), get.CFLAGS(), parameters))

def make(parameters = ''):
    '''make source with given parameters = "all" || "doc" etc.'''
    if system('make {0} {1}'.format(get.makeJOBS(), parameters)):
        raise MakeError(_('Make failed.'))

def fixInfoDir():
    infoDir = '{}/usr/share/info/dir'.format(get.installDIR())
    if can_access_file(infoDir):
        unlink(infoDir)

def fixpc():
    ''' fix .pc files in installDIR()/usr/lib32/pkgconfig'''
    path = "{}/usr/lib32/pkgconfig".format(get.installDIR())
    if isDirectory(path):
        for f in ls("{}/*.pc".format(path)):
            dosed(f, get.emul32prefixDIR(), get.defaultprefixDIR())

def install(parameters = '', argument = 'install'):
    '''install source into install directory with given parameters'''
    args = 'make prefix=%(prefix)s/%(defaultprefix)s \
            datadir=%(prefix)s/%(data)s \
            infodir=%(prefix)s/%(info)s \
            localstatedir=%(prefix)s/%(localstate)s \
            mandir=%(prefix)s/%(man)s \
            sysconfdir=%(prefix)s/%(conf)s \
            %(parameters)s \
            %(argument)s' % {
                                'prefix': get.installDIR(),
                                'defaultprefix': get.defaultprefixDIR(),
                                'man': get.manDIR(),
                                'info': get.infoDIR(),
                                'localstate': get.localstateDIR(),
                                'conf': get.confDIR(),
                                'data': get.dataDIR(),
                                'parameters': parameters,
                                'argument':argument,
                            }

    if system(args):
        raise InstallError(_('Install failed.'))
    else:
        fixInfoDir()

    if get.buildTYPE() == "emul32":
        fixpc()
        if isDirectory("{}/emul32".format(get.installDIR())): removeDir("/emul32")

def rawInstall(parameters = '', argument = 'install'):
    '''install source into install directory with given parameters = PREFIX=%s % get.installDIR()'''
    if system('make {0} {1}'.format(parameters, argument)):
        raise InstallError(_('Install failed.'))
    else:
        fixInfoDir()

    if get.buildTYPE() == "emul32":
        fixpc()
        if isDirectory("{}/emul32".format(get.installDIR())): removeDir("/emul32")

def aclocal(parameters = ''):
    '''generates an aclocal.m4 based on the contents of configure.in.'''
    if system('aclocal {}'.format(parameters)):
        raise RunTimeError(_('Running aclocal failed.'))

def autoconf(parameters = ''):
    '''generates a configure script'''
    if system('autoconf {}'.format(parameters)):
        raise RunTimeError(_('Running autoconf failed.'))

def autoreconf(parameters = ''):
    '''re-generates a configure script'''
    if system('autoreconf {}'.format(parameters)):
        raise RunTimeError(_('Running autoreconf failed.'))

def automake(parameters = ''):
    '''generates a makefile'''
    if system('automake {}'.format(parameters)):
        raise RunTimeError(_('Running automake failed.'))

def autoheader(parameters = ''):
    '''generates templates for configure'''
    if system('autoheader {}'.format(parameters)):
        raise RunTimeError(_('Running autoheader failed.'))
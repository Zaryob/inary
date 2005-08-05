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
#

# Standard Python Modules
import os

# Pisi Modules
from pisi.ui import ui

# ActionsAPI Modules
import get
from shelltools import system
from shelltools import can_access_file
from libtools import gnuconfig_update

class ConfigureError(Exception):
    def __init__(self, Exception):
        ui.error(Exception)
        if can_access_file('config.log'):
            ui.error('\n!!! Please attach the config.log to your bug report:\n%s/config.log\n' % os.getcwd())

class MakeError(Exception):
    def __init__(self, Exception):
        ui.error(Exception)

class InstallError(Exception):
    def __init__(self, Exception):
        ui.error(Exception)

def configure(parameters = ''):
    ''' configure source with given parameters = "--with-nls --with-libusb --with-something-usefull"'''
    if can_access_file('configure'):
        gnuconfig_update()
        
        configure_string = './configure --prefix=/%s --host=%s --mandir=/%s \
            --infodir=/%s --datadir=/%s --sysconfdir=/%s \
                --localstatedir=/%s %s' \
                    % (get.defaultprefixDIR(), get.HOST(), get.manDIR(), 
                        get.infoDIR(), get.dataDIR(), get.confDIR(), 
                            get.localstateDIR(), parameters)
    
        if system(configure_string):
            raise ConfigureError('!!! Configure failed...\n')
    else:
        raise ConfigureError('!!! No configure script found...\n')

def rawConfigure(parameters = ''):
    ''' configure source with given parameters = " --prefix=/usr --libdir=/usr/lib --with-nls"'''
    if can_access_file('configure'):
        gnuconfig_update()

        if system('./configure %s' % parameters):
            raise ConfigureError('!!! Configure failed...\n')
    else:
        raise ConfigureError('!!! No configure script found...\n')
 
def rawConfigureWithPrefix(prefix='', parameters = ''):
    #FIXME: Find another way for this function!
    if can_access_file('configure'):
        gnuconfig_update()

        if system('%s ./configure %s' % ( prefix, parameters)):
            raise ConfigureError('!!! Configure failed...\n')
    else:
        raise ConfigureError('!!! No configure script found...\n')

def compile(parameters = ''):
    system('%s %s %s' % (get.GCC(), get.CFLAGS(), parameters))

def make(parameters = ''):
    if can_access_file('makefile') or can_access_file('Makefile') or can_access_file('GNUmakefile'):
        if system('make %s' % parameters):
            raise MakeError('!!! Make failed...\n')
    else:
        raise MakeError('!!! No Makefile found...\n')

def install(parameters = ''):
    if can_access_file('makefile') or can_access_file('Makefile') or can_access_file('GNUmakefile'):
        install_string = 'make prefix=%(prefix)s/%(defaultprefix)s \
                datadir=%(prefix)s/%(data)s \
                infodir=%(prefix)s/%(info)s \
                localstatedir=%(prefix)s/%(localstate)s \
                mandir=%(prefix)s/%(man)s \
                sysconfdir=%(prefix)s/%(conf)s \
                %(parameters)s \
                install' % {'prefix': get.installDIR(),
                            'defaultprefix': get.defaultprefixDIR(),
                            'man': get.manDIR(),
                            'info': get.infoDIR(),
                            'localstate': get.localstateDIR(),
                            'conf': get.confDIR(),
                            'data': get.dataDIR(),
                            'parameters': parameters}

        if system(install_string):
            raise InstallError('!!! Install failed...\n')
    else:
        raise InstallError('!!! No Makefile found...\n')

def rawInstall(parameters = ''):
    if can_access_file('makefile') or can_access_file('Makefile') or can_access_file('GNUmakefile'):
        if system('make %s install' % parameters):
            raise InstallError('!!! Install failed...\n')
    else:
        raise InstallError('!!! No Makefile found...\n')

def aclocal(parameters = ''):
    system('aclocal %s' % parameters)

def autoconf(parameters = ''):
    system('autoconf %s' % parameters)

def automake(parameters = ''):
    system('automake %s' % parameters)

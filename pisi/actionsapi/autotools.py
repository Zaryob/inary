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

# ActionsAPI Modules
import get
from shelltools import system

def configure(parameters = ''):
    ''' configure source with given parameters = "--with-nls --with-libusb --with-something-usefull"'''

    configure_string = './configure --prefix=/%s --host=%s --mandir=/%s \
            --infodir=/%s --datadir=/%s --sysconfdir=/%s \
                --localstatedir=/%s %s' \
                    % (get.defaultprefixDIR(), get.HOST(), get.manDIR(), 
                        get.infoDIR(), get.dataDIR(), get.confDIR(), 
                            get.localstateDIR(), parameters)
    
    system(configure_string)
    
def rawConfigure(parameters = ''):
    ''' configure source with given parameters = " --prefix=/usr --libdir=/usr/lib --with-nls"'''
    system('./configure %s' % parameters)

#FIXME: Find another way!
def rawConfigureWithPrefix(prefix='', parameters = ''):
    system('%s ./configure %s' % ( prefix, parameters))

def compile(parameters = ''):
    system('%s %s %s' % (get.GCC(), get.CFLAGS(), parameters))

def make(parameters = ''):
    make_string = ('make %s' % parameters)
    system(make_string)

def install(parameters = ''):
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

    system(install_string)

def rawInstall(parameters = ''):
    system('make %s install' % parameters)

def aclocal(parameters = ''):
    system('aclocal %s' % parameters)

def autoconf(parameters = ''):
    system('autoconf %s' % parameters)

def automake(parameters = ''):
    system('automake %s' % parameters)

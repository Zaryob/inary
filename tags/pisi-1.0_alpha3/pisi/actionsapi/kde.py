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

# standard python modules
import os

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import system, can_access_file

class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, Exception):
        ctx.ui.error(Exception)
        if can_access_file('config.log'):
            ctx.ui.error('\n!!! Please attach the config.log to your bug report:\n%s/config.log' % os.getcwd())

class MakeError(pisi.actionsapi.Error):
    def __init__(self, Exception):
        ctx.ui.error(Exception)

class InstallError(pisi.actionsapi.Error):
    def __init__(self, Exception):
        ctx.ui.error(Exception)

def configure(parameters = ''):
    ''' parameters = '--with-nls --with-libusb --with-something-usefull '''
    if can_access_file('configure'):
        args = './configure \
                --prefix=%s \
                --host=%s \
                --with-x \
                --enable-mitshm \
                --with-xinerama \
                --with-qt-dir=%s \
                --enable-mt \
                --with-qt-libraries=%s \
                --enable-final \
                --disable-dependency-tracking \
                --disable-debug \
                %s' % (get.kdeDIR(), get.HOST(), get.qtDIR(), get.qtLIBDIR(), parameters)

        if system(args):
            raise ConfigureError('!!! Configure failed...\n')
    else:
        raise ConfigureError('!!! No configure script found...\n')

def make(parameters = ''):
    '''make source with given parameters = "all" || "doc" etc.'''
    if system('make %s' % parameters):
        raise MakeError('!!! Make failed...\n')

def install(parameters = 'install'):
    if can_access_file('Makefile'):
        args = 'make DESTDIR=%s destdir=%s %s' % (get.installDIR(), get.installDIR(), parameters)
        
        if system(args):
            raise InstallError('!!! Install failed...\n')
    else:
        raise InstallError('!!! No Makefile found...\n')

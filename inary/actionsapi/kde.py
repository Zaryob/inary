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

# standard python modules
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

class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)
        if can_access_file('config.log'):
            ctx.ui.error(_('\n!!! Please attach the config.log to your bug report:\n{}/config.log').format(os.getcwd()))

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

def configure(parameters = ''):
    ''' parameters = '--with-nls --with-libusb --with-something-usefull '''
    if can_access_file('configure'):
        args = './configure \
                --prefix={0.kdeDIR()} \
                --build={0.HOST()} \
                --with-x \
                --enable-mitshm \
                --with-xinerama \
                --with-qt-dir={0.qtDIR()} \
                --enable-mt \
                --with-qt-libraries={0.qtDIR}/lib \
                --disable-dependency-tracking \
                --disable-debug \
                {1}'.format(get, parameters)

        if system(args):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(_('No configure script found.'))

def make(parameters = ''):
    '''make source with given parameters = "all" || "doc" etc.'''
    if system('make {0} {1}'.format(get.makeJOBS(), parameters)):
        raise MakeError(_('Make failed.'))

def install(parameters = 'install'):
    if can_access_file('Makefile'):
        args = 'make DESTDIR={0} destdir={0} {1}'.format(get.installDIR(), parameters)

        if system(args):
            raise InstallError(_('Install failed.'))
    else:
        raise InstallError(_('No Makefile found.'))

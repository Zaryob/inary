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
from pisi.actionsapi.pisitools import dodoc

class CompileError(pisi.actionsapi.Error):
    def __init__(self, Exception):
        ctx.ui.error(Exception)

class InstallError(pisi.actionsapi.Error):
    def __init__(self, Exception):
        ctx.ui.error(Exception)

class RunTimeError(pisi.actionsapi.Error):
    def __init__(self, Exception):
        ctx.ui.error(Exception)

def compile(parameters = ''):
    '''compile source with given parameters.'''
    if system('python setup.py build %s' % (get.installDIR(), parameters)):
        raise CompileError('!!! Make failed...\n')

def install(parameters = ''):
    '''does python setup.py install'''
    if system('python setup.py install --root=%s --no-compile %s' % (get.installDIR(), parameters)):
        raise InstallError('!!! Install failed...\n')

    DDOCS = 'CHANGELOG COPYRIGHT KNOWN_BUGS MAINTAINERS PKG-INFO \
             CONTRIBUTORS LICENSE COPYING* Change* MANIFEST* README*'

    for doc in DDOCS:
        if can_access_file(doc):
            pisitools.dodoc(doc)

def run(parameters = ''):
    '''executes parameters with python'''
    if system('python %s' % (parameters)):
        raise RunTimeError('!!! Running %s failed...\n' % parameters)

# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.

import glob
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
from inary.actionsapi.shelltools import system, can_access_file, unlink, isEmpty
from inary.actionsapi.inarytools import dodoc


class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PythonTools]: " + value)


class CompileError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PythonTools]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PythonTools]: " + value)


class RunTimeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PythonTools]: " + value)


def configure(parameters='', pyVer=''):
    """does python setup.py configure"""
    if system('python{0} setup.py configure {1}'.format(pyVer, parameters)):
        raise ConfigureError(_('Configuration failed.'))


def compile(parameters='', pyVer=''):
    """compile source with given parameters."""
    if system('python{0} setup.py build {1}'.format(pyVer, parameters)):
        raise CompileError(_('Make failed.'))


def install(parameters='', pyVer=''):
    """does python setup.py install"""
    if system('python{0} setup.py install --root={1} --no-compile -O0 {2}'.format(pyVer, get.installDIR(), parameters)):
        raise InstallError(_('Install failed.'))

    docFiles = ('AUTHORS', 'CHANGELOG', 'CONTRIBUTORS', 'COPYING*', 'COPYRIGHT',
                'Change*', 'KNOWN_BUGS', 'LICENSE', 'MAINTAINERS', 'NEWS',
                'README*', 'PKG-INFO')

    for docGlob in docFiles:
        for doc in glob.glob(docGlob):
            if not isEmpty(doc):
                dodoc(doc)


def run(parameters='', pyVer=''):
    """executes parameters with python"""
    if system('python{0} {1}'.format(pyVer, parameters)):
        raise RunTimeError(_('Running \"{}\" failed.').format(parameters))


def fixCompiledPy(lookInto='/usr/lib/{}/'.format(get.curPYTHON())):
    """ cleans *.py[co] from packages """
    for root, dirs, files in os.walk('{0}/{1}'.format(get.installDIR(), lookInto)):
        for compiledFile in files:
            if compiledFile.endswith('.pyc') or compiledFile.endswith('.pyo'):
                if can_access_file('{0}/{1}'.format(root, compiledFile)):
                    unlink('{0}/{1}'.format(root, compiledFile))

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
from inary.actionsapi.shelltools import export
from inary.actionsapi.shelltools import unlink
from inary.actionsapi.shelltools import unlinkDir


class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PerlTools]: " + value)


class MakeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PerlTools]: " + value)


class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[PerlTools]: " + value)


def configure(parameters=''):
    """configure source with given parameters."""
    export('PERL_MM_USE_DEFAULT', '1')
    if can_access_file('Build.PL'):
        if system('perl{0} Build.PL installdirs=vendor destdir={1}'.format(get.curPERL(), get.installDIR())):
            raise ConfigureError(_('Configure failed.'))
    elif can_access_file('Build.PL'):
        if system('perl{0} Makefile.PL {1} PREFIX=/usr INSTALLDIRS=vendor DESTDIR={2}'.format(get.curPERL(), parameters,
                                                                                              get.installDIR())):
            raise ConfigureError(_('Configure failed.'))
    else:
            raise ConfigureError(_('No configure script found. (\"{}\" file not found.)'.format("Build.PL/Makefile.PL")))



def make(parameters=''):
    """make source with given parameters."""
    if can_access_file('Makefile'):
        if system('make {}'.format(parameters)):
            raise MakeError(_('Make failed.'))
    else:
        if system('perl{0} Build {1}'.format(get.curPERL(), parameters)):
            raise MakeError(_('\'perl build\' failed.'))


def install(parameters='install'):
    """install source with given parameters."""
    if can_access_file('Makefile'):
        if system('make {}'.format(parameters)):
            raise InstallError(_('Install failed.'))
    else:
        if system('perl{} Build install'.format(get.curPERL())):
            raise MakeError(_('\'perl install\' failed.'))

    removePacklist()
    removePodfiles()


def removePacklist(path='usr/lib/perl5/'):
    """ cleans .packlist file from perl packages """
    full_path = '{0}/{1}'.format(get.installDIR(), path)
    for root, dirs, files in os.walk(full_path):
        for packFile in files:
            if packFile == ".packlist":
                if can_access_file('{0}/{1}'.format(root, packFile)):
                    unlink('{0}/{1}'.format(root, packFile))
                    removeEmptydirs(root)


def removePodfiles(path='usr/lib/perl5/'):
    """ cleans *.pod files from perl packages """
    full_path = '{0}/{1}'.format(get.installDIR(), path)
    for root, dirs, files in os.walk(full_path):
        for packFile in files:
            if packFile.endswith(".pod"):
                if can_access_file('{0}/{1}'.format(root, packFile)):
                    unlink('{0}/{1}'.format(root, packFile))
                    removeEmptydirs(root)


def removeEmptydirs(d):
    """ remove empty dirs from perl package if exists after deletion .pod and .packlist files """
    if not os.listdir(d) and not d == get.installDIR():
        unlinkDir(d)
        d = d[:d.rfind("/")]
        removeEmptydirs(d)

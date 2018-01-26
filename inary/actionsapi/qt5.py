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

import glob
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# Inary Modules
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi

# ActionsAPI Modules
from inary.actionsapi import get
from inary.actionsapi import cmaketools
from inary.actionsapi import shelltools

basename = "qt5"

prefix = "/{}".format(get.defaultprefixDIR())
libdir = "{}/lib".format(prefix)
libexecdir = "{}/libexec".format(prefix)
sysconfdir= "/etc"
bindir = "{}/bin".format(prefix)
includedir = "{}/include".format(prefix)

# qt5 spesific variables

headerdir = "{}/include/{}".format(prefix, basename)
datadir = "{}/share/{}".format(prefix, basename)
docdir = "/{}/{}".format(get.docDIR(), basename)
archdatadir = "{}/{}".format(libdir, basename)
examplesdir = "{}/{}/examples".format(libdir, basename)
importdir = "{}/{}/imports".format(libdir, basename)
plugindir = "{}/{}/plugins".format(libdir, basename)
qmldir = "{}/{}/qmldir".format(libdir, basename)
testdir = "{}/share/{}".format(prefix, basename)
translationdir = "{}/translations".format(datadir)

qmake = "{}/qmake-qt5" % bindir

class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def configure(projectfile='', parameters='', installPrefix=prefix):
    if projectfile != '' and not shelltools.can_access_file(projectfile):
        raise ConfigureError(_("Project file '{}' not found.").format(projectfile))

    profiles = glob.glob("*.pro")
    if len(profiles) > 1 and projectfile == '':
        raise ConfigureError(_("It seems there are more than one .pro file, you must specify one. (Possible .pro files: {})").format(", ".join(profiles)))

    shelltools.system("{0} -makefile {1} PREFIX='{2}' QMAKE_CFLAGS+='{3.CFLAGS()}' QMAKE_CXXFLAGS+='{3.CXXFLAGS()}' {5}".format(qmake, projectfile, installPrefix, get, parameters))

def make(parameters=''):
    cmaketools.make(parameters)

def install(parameters='', argument='install'):
    cmaketools.install('INSTALL_ROOT="{0}" {1}'.format(get.installDIR(), parameters), argument)


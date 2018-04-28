# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
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

basename = "qt4"

prefix = "/{}".format(get.defaultprefixDIR())
libdir = "{}/lib".format(prefix)
bindir = "{}/bin".format(prefix)
datadir = "{0}/share/{1}".format(prefix, basename)
includedir = "{}/include".format(prefix)
docdir = "/{0}/{1}".format(get.docDIR(), basename)
examplesdir = "{0}/{1}/examples".format(libdir, basename)
demosdir = "{0}/{1}/demos".format(libdir, basename)
importdir = "{0}/{1}/imports".format(libdir, basename)
plugindir = "{0}/{1}/plugins".format(libdir, basename)
translationdir = "{}/translations".format(datadir)
sysconfdir= "/etc"
qmake = "{}/qmake".format(bindir)

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

    shelltools.system("{0} -makefile {1} PREFIX='{2}' QMAKE_CFLAGS+='{3.CFLAGS()}' QMAKE_CXXFLAGS+='{3.CXXFLAGS()}' {4}".format(qmake, projectfile, installPrefix, get, parameters))

def make(parameters=''):
    cmaketools.make(parameters)

def install(parameters='', argument='install'):
    cmaketools.install('INSTALL_ROOT="{0}" {1}'.format(get.installDIR(), parameters), argument)

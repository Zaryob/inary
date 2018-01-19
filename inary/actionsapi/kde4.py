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

# ActionsAPI Modules
from inary.actionsapi import get
from inary.actionsapi import cmaketools
from inary.actionsapi import shelltools

basename = "kde4"

prefix = "/{}".format(get.defaultprefixDIR())
libdir = "{}/lib".format(prefix)
bindir = "{}/bin".format(prefix)
modulesdir = "{0}/{1}".format(libdir, basename)
libexecdir = "{}/libexec".format(modulesdir)
iconsdir = "{}/share/icons".format(prefix)
applicationsdir = "{0}/share/applications/{1}".format(prefix, basename)
mandir = "/{}" % get.manDIR()
sharedir = "{0}/share/{1}".format(prefix, basename)
appsdir = "{}/apps".format(sharedir)
configdir = "{}/config".format(sharedir)
sysconfdir= "/etc"
servicesdir = "{}/services".format(sharedir)
servicetypesdir = "{}/servicetypes".format(sharedir)
includedir = "{0}/include/{1}".format(prefix, basename)
docdir = "/{0}/{1}".format(get.docDIR(), basename)
htmldir = "{}/html".format(docdir)
wallpapersdir = "{}/share/wallpapers".format(prefix)

def configure(parameters = '', installPrefix = prefix, sourceDir = '..'):
    ''' parameters -DLIB_INSTALL_DIR="hede" -DSOMETHING_USEFUL=1'''

    shelltools.makedirs("build")
    shelltools.cd("build")

    cmaketools.configure("-DDATA_INSTALL_DIR:PATH={0} \
            -DINCLUDE_INSTALL_DIR:PATH={1} \
            -DCONFIG_INSTALL_DIR:PATH={2} \
            -DLIBEXEC_INSTALL_DIR:PATH={3} \
            -DSYSCONF_INSTALL_DIR:PATH={4} \
            -DHTML_INSTALL_DIR:PATH={5} \
            -DMAN_INSTALL_DIR:PATH={6} \
            -DCMAKE_SKIP_RPATH:BOOL=ON \
            -DLIB_INSTALL_DIR:PATH={7} {8}".format(appsdir, includedir, configdir, libexecdir, sysconfdir, htmldir, mandir, libdir, parameters), installPrefix, sourceDir)

    shelltools.cd("..")

def make(parameters = ''):
    cmaketools.make('-C build {}'.format(parameters))

def install(parameters = '', argument = 'install'):
    cmaketools.install('-C build {}'.format(parameters), argument)

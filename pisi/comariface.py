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
# Authors: Baris Metin <baris@uludag.org.tr>
#          Gurer Ozen <gurer@uludag.org.tr>

import comar

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx

def run_postinstall(package_name):
    "run postinstall scripts trough COMAR"

    com = ctx.comard
    assert(com)
    ctx.ui.info(_("Running postinstall script for %s") % package_name)
    com.call_package("System.Package.postInstall", package_name)
    while 1:
        reply = com.read_cmd()
        if reply[0] == com.RESULT:
            break
        elif reply[0] == com.NONE: # package has no postInstall script
            break
        elif reply[0] == com.FAIL:
            e = _("COMAR.call_package(System.Pakcage.postInstall, %s) failed!: %s") % (
                self.metadata.package.name, reply[2])
            raise InstallError, e
        else:
            raise InstallError, _("COMAR.call_package ERROR: %d") % reply[0]

def run_preremove(package_name):
    com = ctx.comard
    assert(com)
    com.remove(package_name)
    while 1:
        reply = com.read_cmd()
        if reply[0] == com.RESULT:
            break
        elif reply[1] == com.ERROR:
            raise Error, "COMAR.remove failed!"

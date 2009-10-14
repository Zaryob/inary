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

import pisi
import pisi.context as ctx

class Error(pisi.Error):
    pass

def make_com():
    # FIXME: just try for others (that don't use comar)
    try:
        import comar
        comard = comar.Link()
        return comard
    except ImportError:
        raise Error(_("COMAR: comard not fully installed"))
    except comar.Error:
        raise Error(_("COMAR: comard not running or defunct"))

def register(pcomar, name, path):
    ctx.ui.info(_("Registering COMAR script %s") % pcomar.script)
    com = make_com()
    assert(com)
    com.register(pcomar.om, name, path)

    while 1:
        reply = com.read_cmd()
        if reply[0] == com.RESULT:
            break
        else:
            raise Error, _("COMAR.register ERROR!")


def run_postinstall(package_name):
    "run postinstall scripts trough COMAR"

    com = make_com()
    assert(com)
    ctx.ui.info(_("Running post-install script for %s") % package_name)
    com.call_package("System.Package.postInstall", package_name)
    while 1:
        reply = com.read_cmd()
        if reply[0] == com.RESULT:
            break
        elif reply[0] == com.NONE: # package has no postInstall script
            break
        elif reply[0] == com.FAIL:
            e = _("COMAR.call_package(System.Package.postInstall, %s) failed!: %s") % (
                package_name, reply[2])
            raise Error, e
        else:
            raise Error, _("COMAR.call_package ERROR: %d") % reply[0]

def run_preremove(package_name):

    com = make_com()
    assert(com)

    # First, call preRemove script!
    ctx.ui.info(_("Running pre-remove script for %s") % package_name)
    com.call_package("System.Package.preRemove", package_name)
    while 1:
        reply = com.read_cmd()
        if reply[0] == com.RESULT:
            break
        elif reply[0] == com.NONE: # package has no preRemove script
            break
        elif reply[0] == com.FAIL:
            e = _("COMAR.call_package(System.Package.preRemove, %s) failed!: %s") % (
                package_name, reply[2])
            raise Error, e
        else:
            raise Error, _("COMAR.call_package ERROR: %d") % reply[0]

    # and then, remove package's Comar Scripts...
    ctx.ui.info(_("Unregistering COMAR scripts for %s") % package_name)
    com.remove(package_name)
    while 1:
        reply = com.read_cmd()
        if reply[0] == com.RESULT:
            break
        elif reply[1] == com.ERROR:
            raise Error, "COMAR.remove failed!"

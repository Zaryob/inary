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
# Authors: Baris Metin <baris@pardus.org.tr>
#          Gurer Ozen <gurer@pardus.org.tr>

import comar

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx

class Error(pisi.Error):
    pass

def make_com():
    try:
        import comar

        if ctx.comar_sockname:
            comard = comar.Link(sockname=ctx.comar_sockname)
        else:
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

def wait_comar():
    import socket, time
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    timeout = 5
    while timeout > 0:
        try:
            if ctx.comar_sockname:
                sock.connect(ctx.comar_sockname)
            else:
                sock.connect("/var/run/comar.socket")
            return True
        except:
            timeout -= 0.2
        time.sleep(0.2)
    return False

def run_postinstall(package_name):
    "run postinstall scripts trough COMAR"

    com = make_com()
    assert(com)
    ctx.ui.info(_("Running post-install script for %s") % package_name)
    com.call_package("System.Package.postInstall", package_name)
    while 1:
        try:
            reply = com.read_cmd()
        except:
            # Comar postInstall does a "service comar restart" which cuts
            # our precious communication link, so we waitsss
            if package_name == "comar":
                if not wait_comar():
                    raise Error, _("Could not restart Comar")
                return
            else:
                raise Error, _("Comar daemon closed the connection")
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

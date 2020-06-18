# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Standard Python Modules
import os
import re
import shutil

# Inary Modules
import inary.context as ctx

# ActionsAPI Modules
import inary.actionsapi
import inary.actionsapi.get as get
import inary.actionsapi.autotools as autotools
import inary.actionsapi.shelltools as shelltools
import inary.actionsapi.inarytools as inarytools

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[KernelTools]" + value)

def save_headers():
    autotools.make("INSTALL_HDR_PATH={}/headers headers_install".format(get.pkgDIR()))
    shelltools.system("find dest/include \( -name .install -o -name ..install.cmd \) -delete")
    shelltools.system("cp -rv dest/include/* {}/usr/include".format(get.pkgDIR()))

def install_headers():
    shelltools.system("mv -v {}/* {}/usr/include".format(get.pkgDIR(), get.installDIR()))


def generate_version():
    pass

def configure():
    pass

def build():
    pass

def modules_install():
    pass

def bzimage_install(bzImage=""):
    pass

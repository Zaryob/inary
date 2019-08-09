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

import inary.actionsapi
import inary.util as util
import inary.context as ctx
from inary.actionsapi import get
from inary.actionsapi.shelltools import can_access_file
from inary.actionsapi.shelltools import system

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

class MesonError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)


def meson_configure(parameters=""):
    if can_access_file('meson.build'):
        prefix = get.defaultprefixDIR()
        args = "meson \
              --prefix=/{0} \
              --buildtype=plain \
              --libdir=/{0}/lib{1} \
              --libexecdir={2} \
              --sysconfdir={3} \
              --localstatedir={4} \
              {5} inaryPackageBuild".format(
            prefix,
            "32 " if get.buildTYPE() == "emul32" else "",
            get.libexecDIR(),
            get.confDIR(),
            get.localstateDIR(),
            parameters)

        if system(args):
            raise MesonError(_('[Meson]: Configure failed.'))
    else:
        raise MesonError(_('[Meson]: Configure script cannot be reached'))


def ninja_build(parameters=""):
    if system("ninja {} {} -C inaryPackageBuild".format(get.makeJOBS(), parameters)):
        raise MesonError(_("[Ninja]: Build failed."))


def ninja_install(parameters=""):
    insdir = util.join_path(get.installDIR(), "emul32") if get.buildTYPE() == "emul32" else get.installDIR()
    if system('DESTDIR="{}" ninja install {} -C inaryPackageBuild'.format(insdir, get.makeJOBS())):
        raise MesonError(_("[Ninja]: Installation failed."))


def ninja_check():
    if system('ninja test {} -C inaryPackageBuild'.format(get.makeJOBS())):
        raise MesonError(_("[Ninja]: Test failed"))

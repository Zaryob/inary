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

# Inary Modules
import inary.context as ctx
import inary.util as util

# ActionsAPI Modules
import inary.actionsapi
from inary.actionsapi import get
from inary.actionsapi.shelltools import cd
from inary.actionsapi.shelltools import ls
from inary.actionsapi.shelltools import copy
from inary.actionsapi.inarytools import dosed
from inary.actionsapi.shelltools import system
from inary.actionsapi.shelltools import makedirs
from inary.actionsapi.inarytools import removeDir
from inary.actionsapi.shelltools import isDirectory
from inary.actionsapi.shelltools import can_access_file

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class MesonError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[MesonTools]: " + value)


class ConfigureError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[MesonTools]: " + value)


class NinjaBuildError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error("[MesonTools]: " + value)


def fixpc():
    """ fix .pc files in installDIR()/usr/lib32/pkgconfig"""
    path = "{}/usr/lib32/pkgconfig".format(get.installDIR())
    if isDirectory(path):
        for f in ls("{}/*.pc".format(path)):
            dosed(f, get.emul32prefixDIR(), get.defaultprefixDIR())


def configure(parameters="", type="meson"):
    if type == "meson":
        meson_configure(parameters)
    else:
        cmake_configure(parameters)


def meson_configure(parameters=""):
    if can_access_file('meson.build'):
        prefix = get.defaultprefixDIR()
        args = "meson \
              --prefix=/{0} \
              --buildtype=plain \
              --libdir=/{0}/lib{1} \
              --libexecdir=/{2} \
              --sysconfdir=/{3} \
              --localstatedir=/{4} \
              {5} inaryPackageBuild".format(
            prefix,
            "32 " if get.buildTYPE() == "emul32" else "",
            get.libexecDIR(),
            get.confDIR(),
            get.localstateDIR(),
            parameters)

        if system(args):
            raise MesonError(_('Configure failed.'))
    else:
        raise ConfigureError(
            _('No configure script found. (\"{}\" file not found.)'.format("meson.build")))


def cmake_configure(parameters=""):
    makedirs("inaryPackageBuild")
    cd("inaryPackageBuild")

    if can_access_file(util.join_path("..", 'CMakeLists.txt')):
        args = 'cmake -DCMAKE_INSTALL_PREFIX=/{0} \
                      -DCMAKE_INSTALL_LIBDIR={1} \
                      -DCMAKE_C_FLAGS="{6} {2}" \
                      -DCMAKE_CXX_FLAGS="{6} {3}" \
                      -DCMAKE_LD_FLAGS="{4}" \
                      -DCMAKE_BUILD_TYPE=RelWithDebInfo {5} -G Ninja ..'.format(get.defaultprefixDIR(),
                                                                                "/usr/lib32 " if get.buildTYPE() == "emul32" else "/usr/lib",
                                                                                get.CFLAGS(),
                                                                                get.CXXFLAGS(),
                                                                                get.LDFLAGS(),
                                                                                parameters,
                                                                                "-m32" if get.buildTYPE() == "emul32" else "-m64")

        if system(args):
            raise ConfigureError(_('CMake configure failed.'))
    else:
        raise ConfigureError(
            _('No configure script found. (\"{}\" file not found.)'.format("CMakeLists.txt")))


def make(parameters=""):
    ninja_build(parameters)


def ninja_build(parameters=""):
    if system("ninja {} {} -C inaryPackageBuild".format(get.makeJOBS(), parameters)):
        raise NinjaBuildError(_("Build failed."))
    if get.buildTYPE() == "emul32":
        fixpc()
        if isDirectory("{}/emul32".format(get.installDIR())):
            removeDir("/emul32")


def install(parameters=""):
    ninja_install(parameters)


def ninja_install(parameters=""):
    insdir = util.join_path(
        get.installDIR(),
        "emul32") if get.buildTYPE() == "emul32" else get.installDIR()
    if system(
            'DESTDIR="{}" ninja install {} -C inaryPackageBuild'.format(insdir, get.makeJOBS())):
        raise NinjaBuildError(_("Install failed."))
    if isDirectory("{}/emul32".format(get.installDIR())):
        if isDirectory("{}/emul32/lib32".format(get.installDIR())):
            copy("{}/emul32/lib32".format(get.installDIR()),
                 "{}/".format(get.installDIR()))
        if isDirectory("{}/emul32/usr/lib32".format(get.installDIR())):
            copy("{}/emul32/usr/lib32".format(get.installDIR()),
                 "{}/usr/".format(get.installDIR()))
        removeDir("/emul32")


def check():
    ninja_check()


def ninja_check():
    if system('ninja test {} -C inaryPackageBuild'.format(get.makeJOBS())):
        raise MesonError(_("Check failed."))

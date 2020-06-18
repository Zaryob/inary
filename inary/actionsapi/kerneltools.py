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
from inary.util import join_path

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
    shelltools.system("find include \( -name .install -o -name ..install.cmd \) -delete")
    shelltools.system("cp -rv include/* {}/headers/include/".format(get.pkgDIR()))

def install_headers():
    os.makedirs(join_path(get.installDIR(), "/usr/"))
    shelltools.system("cp -rv {}/headers/* {}/usr/include".format(get.pkgDIR(), get.installDIR()))


def generateVersion():
    autotools.make("-s kernelrelease > version")


def dumpVersion():
    # Writes the specific kernel version into /etc/kernel
    destination = os.path.join(get.installDIR(), "etc/kernel/")
    if not os.path.exists(destination):
        os.makedirs(destination)
    inarytools.insinto("/etc/kernel", "version", destinationFile=get.srcNAME())

def __getKernelARCH():
    return get.ARCH()


def configure(ExtraVersion=""):

    inarytools.dosed(
        "Makefile",
        "EXTRAVERSION =.*",
        "EXTRAVERSION = {}".format(
            ExtraVersion))
    # Configure the kernel interactively if
    # configuration contains new options
    autotools.make("ARCH={} oldconfig".format(__getKernelARCH()))

    # Check configuration with listnewconfig
    try:
        autotools.make("ARCH={} listnewconfig".format(__getKernelARCH()))
    except BaseException:
        pass

def build(debugSymbols=False):
    extra_config = []
    if debugSymbols:
        # Enable debugging symbols (-g -gdwarf2)
        extra_config.append("CONFIG_DEBUG_INFO=y")

    autotools.make(
        "ARCH={0} {1}".format(
            __getKernelARCH(),
            " ".join(extra_config)))


def install(suffix=""):
    if not suffix:
        suffix=get.srcNAME()+get.srcVERSION()

    generateVersion()
    # Dump kernel version under /etc/kernel
    dumpVersion()

    # Install the modules
    # mod-fw= avoids firmwares from installing
    # Override DEPMOD= to not call depmod as it will be called
    # during module-init-tools' package handler
    autotools.rawInstall("INSTALL_MOD_PATH={}/".format(get.installDIR()),
                         "DEPMOD=/bin/true modules_install mod-fw=")

    # Install Module.symvers and System.map here too
    shutil.copy("Module.symvers",
                "{0}/lib/modules/{1}{2}/".format(get.installDIR(),get.srcVERSION() ,suffix))

    shutil.copy(
        "System.map",
                "{0}/lib/modules/{1}{2}/".format(get.installDIR(),get.srcVERSION() ,suffix))

    # Create extra/ and updates/ subdirectories
    for _dir in ("extra", "updates"):
        inarytools.dodir("/lib/modules/{0}{1}/{2}".format(get.srcVERSION(), suffix, _dir))


def modules_install():
    pass

def bzimage_install(suffix=""):
    # Install kernel image
    if not suffix:
        suffix=get.srcNAME()+get.srcVERSION()

    inarytools.insinto(
        "/boot/",
        "arch/x86/boot/bzImage",
        "{}".format(suffix))

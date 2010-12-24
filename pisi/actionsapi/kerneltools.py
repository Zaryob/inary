# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Standard Python Modules
import os
import re
import shutil

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get          as get
import pisi.actionsapi.autotools    as autotools
import pisi.actionsapi.pisitools    as pisitools
import pisi.actionsapi.shelltools   as shelltools


class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

# Internal helpers

def __getAllSupportedFlavours():
    if os.path.exists("/etc/kernel"):
        return os.listdir("/etc/kernel")

#################
# Other helpers #
#################

def __getFlavour():
    try:
        flavour = get.srcNAME().split("kernel-")[1]
    except IndexError:
        return ""
    else:
        return flavour

def __getModuleFlavour():
    for fl in [_f for _f in __getAllSupportedFlavours() if "-" in _f]:
        try:
            if fl.split("-")[1] == get.srcNAME().split("-")[1]:
                return fl
        except IndexError:
            # the package is not a module, may be a userspace application
            # needing the kernel sources/headers for only reference.
            pass

    return "kernel"

def __getKernelARCH():
    """i386 is relevant for our i686 architecture."""
    return get.ARCH().replace("i686", "i386")

def __getSuffix():
    """Read and return the value read from .suffix file."""
    return open(".suffix", "r").read().strip()

def __getExtraVersion(abiVersion):
    extraversion = ""
    try:
        # if successful, this is something like:
        # .1 for 2.6.30.1
        # _rc8 for 2.6.30_rc8
        extraversion = re.split("2.[0-9].[0-9]{2}([._].*)", get.srcVERSION())[1]
    except IndexError:
        # e.g. if version == 2.6.30
        pass

    # abiVersion will be passed from actions.py e.g. like the old release numbers
    extraversion += "-%s" % abiVersion

    # Append pae, default, rt, etc. to the extraversion if available
    if __getFlavour():
        extraversion += "-%s" % __getFlavour()

    return extraversion

#######################
# Configuration stuff #
#######################

def getKernelVersion(flavour=None):
    # Returns the KVER information to use with external module compilation
    # This is something like 2.6.30_rc7-119 which will be appended to /lib/modules.
    # if flavour==None, it will return the KVER in the /etc/kernel/kernel file else,
    # /etc/kernel/<flavour>.
    # If it fails, it will return the running kernel version.

    # Try to detect module flavour
    if not flavour:
        flavour = __getModuleFlavour()

    kverfile = os.path.join("/etc/kernel", flavour)

    if os.path.exists(kverfile):
        return open(kverfile, "r").read().strip()
    else:
        # Fail
        raise ConfigureError(_("Can't find kernel version information file %s.") % kverfile)

def configure(abiVersion):
    # Copy the relevant configuration file
    shutil.copy("configs/kernel-%s-config" % get.ARCH(), ".config")

    # Set EXTRAVERSION
    pisitools.dosed("Makefile", "EXTRAVERSION =.*", "EXTRAVERSION = %s" % __getExtraVersion(abiVersion))

    # Create .suffix file which will contain __getSuffix()'s return value
    suffix = "%s-%s" % (get.srcVERSION(), abiVersion)
    if __getFlavour():
        suffix += "-%s" % __getFlavour()
    open(".suffix", "w").write(suffix)

    # Configure the kernel interactively if
    # configuration contains new options
    autotools.make("ARCH=%s oldconfig" % __getKernelARCH())

    # Check configuration with nonint_oldconfig
    autotools.make("ARCH=%s nonint_oldconfig" % __getKernelARCH())

def updateKConfig():
    # Call this to set newly added symbols to their defaults after sedding some KConfig
    # variables.

    # Grr ugly but no solution.
    shelltools.system('yes "" | make oldconfig')


###################################
# Building and installation stuff #
###################################

def dumpVersion():
    # Writes the specific kernel version into /etc/kernel
    destination = os.path.join(get.installDIR(), "etc/kernel/")
    if not os.path.exists(destination):
        os.makedirs(destination)

    open(os.path.join(destination, get.srcNAME()), "w").write(__getSuffix())


def build(debugSymbols=False):
    extra_config = []
    if debugSymbols:
        # Enable debugging symbols (-g -gdwarf2)
        extra_config.append("CONFIG_DEBUG_INFO=y")

    autotools.make("ARCH=%s %s" % (__getKernelARCH(), " ".join(extra_config)))


def install():
    suffix = __getSuffix()

    # Dump kernel version under /etc/kernel
    dumpVersion()

    # Install kernel image
    pisitools.insinto("/boot/", "arch/x86/boot/bzImage", "kernel-%s" % suffix)

    # Install the modules
    # mod-fw= avoids firmwares from installing
    # Override DEPMOD= to not call depmod as it will be called
    # during module-init-tools' package handler
    autotools.rawInstall("INSTALL_MOD_PATH=%s/" % get.installDIR(),
                         "DEPMOD=/bin/true modules_install mod-fw=")

    # Remove symlinks first
    pisitools.remove("/lib/modules/%s/source" % suffix)
    pisitools.remove("/lib/modules/%s/build" % suffix)

    # Install Module.symvers and System.map here too
    shutil.copy("Module.symvers", "%s/lib/modules/%s/" % (get.installDIR(), suffix))
    shutil.copy("System.map", "%s/lib/modules/%s/" % (get.installDIR(), suffix))

    # Create extra/ and updates/ subdirectories
    for _dir in ("extra", "updates"):
        pisitools.dodir("/lib/modules/%s/%s" % (suffix, _dir))


def installHeaders(extraHeaders=None):
    """ Install the files needed to build out-of-tree kernel modules. """

    extras = ["drivers/media/dvb/dvb-core",
              "drivers/media/dvb/frontends",
              "drivers/media/video"]

    if extraHeaders:
        extras.extend(extraHeaders)

    pruned = ["include", "scripts"]
    wanted = ["Makefile*", "Kconfig*", "Kbuild*", "*.sh", "*.pl", "*.lds"]

    suffix = __getSuffix()
    headersDirectoryName = "usr/src/linux-headers-%s" % suffix

    # Get the destination directory for header installation
    destination = os.path.join(get.installDIR(), headersDirectoryName)
    shelltools.makedirs(destination)

    # First create the skel
    find_cmd = "find . -path %s -prune -o -type f \( -name %s \) -print" % \
                (
                    " -prune -o -path ".join(["'./%s/*'" % l for l in pruned]),
                    " -o -name ".join(["'%s'" % k for k in wanted])
                ) + " | cpio -pVd --preserve-modification-time %s" % destination

    shelltools.system(find_cmd)

    # Install additional headers
    for headers in extras:
        shelltools.system("cp -a %s/*.h %s/%s" % (headers, destination, headers))

    # Install remaining headers
    shelltools.system("cp -a scripts include %s" % destination)

    # Cleanup scripts directory
    shelltools.system("rm -rf %s/scripts/*.o" % destination)
    shelltools.system("rm -rf %s/scripts/*/*.o" % destination)

    # Finally copy the include directories found in arch/
    shelltools.system("(find arch -name include -type d -print | \
                        xargs -n1 -i: find : -type f) | \
                        cpio -pd --preserve-modification-time %s" % destination)

    # Copy Modules.symvers and System.map
    shutil.copy("Module.symvers", "%s/" % destination)
    shutil.copy("System.map", "%s/" % destination)

    # Copy .config file which will be needed by some external modules
    shutil.copy(".config", "%s/" % destination)

    # Unset CONFIG_DEBUG_INFO if it's set in the kernel configuration
    # pisitools.dosed(".config", ".*CONFIG_DEBUG_INFO=.*", "# CONFIG_DEBUG_INFO is not set")

    # Settle the correct build symlink to this headers
    pisitools.dosym("/%s" % headersDirectoryName, "/lib/modules/%s/build" % suffix)
    pisitools.dosym("build", "/lib/modules/%s/source" % suffix)


def installLibcHeaders(excludes=None):
    headers_tmp = os.path.join(get.installDIR(), 'tmp-headers')
    headers_dir = os.path.join(get.installDIR(), 'usr/include')

    make_cmd = "O=%s INSTALL_HDR_PATH=%s/install" % (headers_tmp, headers_tmp)

    # Cleanup temporary header directory
    shelltools.system("rm -rf %s" % headers_tmp)

    # Create directories
    shelltools.makedirs(headers_tmp)
    shelltools.makedirs(headers_dir)

    # make defconfig and install the headers
    autotools.make("%s defconfig" % make_cmd)
    autotools.rawInstall(make_cmd, "headers_install")

    oldwd = os.getcwd()

    shelltools.cd(os.path.join(headers_tmp, "install", "include"))
    shelltools.system("find . -name '.' -o -name '.*' -prune -o -print | \
                       cpio -pVd --preserve-modification-time %s" % headers_dir)

    # Remove sound/ directory which is installed by alsa-headers
    shelltools.system("rm -rf %s/sound" % headers_dir)

    # Remove possible excludes given by actions.py
    if excludes:
        shelltools.system("rm -rf %s" % " ".join(["%s/%s" % (headers_dir, exc.strip("/")) for exc in excludes]))

    shelltools.cd(oldwd)

    # Remove tmp directory
    shelltools.system("rm -rf %s" % headers_tmp)

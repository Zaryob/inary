# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, TUBITAK/UEKAE
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


# Internal helpers for versioning stuff

def __getFlavour():
    flavour = ""
    try:
        flavour = get.srcNAME().split("kernel-")[1]
    except IndexError:
        pass

    return flavour

def __getSuffix():
    # Set suffix, e.g. "2.6.29_rc8-default"
    suffix = "%s-%s" % (get.srcVERSION(), get.srcRELEASE())
    if __getFlavour():
        suffix += "-%s" % __getFlavour()

    return suffix

def __getExtraVersion():
    extraversion = ""
    try:
        # if successful, this is something like:
        # .1 for 2.6.30.1
        # _rc8 for 2.6.30_rc8
        extraversion = re.split("2.[0-9].[0-9]{2}([._].*)", get.srcVERSION())[1]
    except IndexError:
        # e.g. if version == 2.6.30
        pass

    extraversion += "-%s" % get.srcRELEASE()

    # Append pae, default, rt, etc. to the extraversion if available
    if __getFlavour():
        extraversion += "-%s" % __getFlavour()

    return extraversion


# Public callables

def configure():
    # Set EXTRAVERSION
    extraversion = __getExtraVersion()

    # I don't know what for but let's clean *.orig files
    shelltools.system("find . -name \"*.orig\" | xargs rm -f")

    pisitools.dosed("Makefile", "EXTRAVERSION =.*", "EXTRAVERSION = %s" % extraversion)

    # Configure the kernel
    if os.getenv("MENUCONFIG"):
        autotools.make("menuconfig")
    else:
        autotools.make("silentoldconfig")

def build():
    autotools.make()

def install():
    suffix = __getSuffix()

    # Check if loadable module support is available or not before doing module specific tasks
    if re.search("CONFIG_MODULES=y", open(".config", "r").read().strip()):

        # Install the modules into /lib/modules
        autotools.rawInstall("INSTALL_MOD_PATH=%s/" % get.installDIR(),
                             "modules_install")

        # Install Module.symvers and System.map
        pisitools.insinto("/lib/modules/%s/" % suffix, "System.map")
        pisitools.insinto("/lib/modules/%s/" % suffix, "Module.symvers")

        # Remove wrong symlinks
        pisitools.remove("/lib/modules/%s/source" % suffix)
        pisitools.remove("/lib/modules/%s/build" % suffix)



    # Install kernel image
    # TODO: For supporting more architectures in the future, we'll need a more
    # flexible method here instead of hardcoding x86.
    pisitools.insinto("/boot/", "arch/x86/boot/bzImage", "kernel-%s" % suffix)


def installHeaders(extra=[]):
    """ Install the files needed to build out-of-tree kernel modules. """

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
                ) + " | cpio -pd --preserve-modification-time %s" % destination

    shelltools.system(find_cmd)

    # Install additional headers passed by actions.py
    for d in extra:
        shelltools.system("cp -a %s/*.h %s/%s" % (d, destination, d))

    # Install remaining headers
    shelltools.system("cp -a scripts include %s" % destination)

    # Finally copy the include directories found in arch/
    shelltools.system("(find arch -name include -type d -print | \
                        xargs -n1 -i: find : -type f) | \
                        cpio -pd --preserve-modification-time %s" % destination)

    # Settle the correct build symlink to this headers
    pisitools.dosym("/%s" % headersDirectoryName, "/lib/modules/%s/build" % suffix)

def installSource():
    destination = "usr/src/linux-source-%s" %  __getSuffix()

    pisitools.dodir("/usr/src")
    shelltools.copytree("../%s/" % os.path.basename(get.curDIR()), os.path.join(get.installDIR(), destination))

    # Cleanup the installed source
    shelltools.cd(os.path.join(get.installDIR(), destination))
    autotools.make("clean")
    autotools.make("modules_prepare")

def cleanModuleFiles():
    """ Cleans module.* files generated by depmod """
    # Remove modules.* files, they will be autogenerated during pakhandler.
    # TODO: Ubuntu doesn't remove modules.order, reinvestigate.
    pisitools.remove("/lib/modules/%s/modules.*" % __getSuffix())

def mkinitramfs():
    """ Create and install the initramfs image into the package. This will hopefully be done on user's system. """
    shelltools.system("/sbin/mkinitramfs kernel=%s --full --root-dir=%s --output=%s/boot" % (__getSuffix(), get.installDIR(), get.installDIR()))

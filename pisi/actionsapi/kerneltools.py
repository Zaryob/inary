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

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import system
from pisi.actionsapi.shelltools import makedirs
from pisi.actionsapi.shelltools import copytree

def installHeaders(extra=[]):
    """ Install the files needed to build out-of-tree kernel modules. """
    pruned = ["include", "scripts"]
    wanted = ["Makefile*", "Kconfig*", "Kbuild*", "*.sh", "*.pl", "*.lds"]

    destination = "%s/usr/src/linux-headers" % get.installDIR()
    makedirs(destination)

    # First create the skel
    find_cmd = "find . -path %s -prune -o -type f \( -name %s \) -print" % \
                (
                    " -prune -o -path ".join(["'./%s/*'" % l for l in pruned]),
                    " -o -name ".join(["'%s'" % k for k in wanted])
                ) + " | cpio -pd --preserve-modification-time %s" % destination

    system(find_cmd)

    # Install additional headers passed by actions.py
    for d in extra:
        system("cp -a %s/*.h %s/%s" % (d, destination, d))

    # Install remaining headers
    system("cp -a scripts include %s" % destination)

    # Finally copy the include directories found in arch/
    system("(find arch -name include -type d -print | \
            xargs -n1 -i: find : -type f) | \
            cpio -pd --preserve-modification-time %s" % destination)

def installSource():
    pass

def installDocumentation():
    pass

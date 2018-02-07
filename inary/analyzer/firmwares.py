# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import sys
import inary
import inary.context as ctx
import inary.util

#Gettext
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


FW_PATH = "/lib/firmware"
INSTALDB = inary.db.installdb.InstallDB()
COMPONENTDB = inary.db.componentdb.ComponentDB()

class Error(inary.Error):
    pass

def get_firmwares():
    ctx.ui.info(inary.util.colorize("Extracting firmware list for {}...".format(os.uname()[2]), "green"))
    d = {}
    modules = [os.path.basename(mod.replace(".ko", "")) for mod in \
            os.popen("modprobe -l").read().strip().split("\n")]
    for mod in modules:
        fws = os.popen("modinfo -F firmware {}".format(mod)).read().strip()
        if fws:
            try:
                d[mod].extend(fws.split("\n"))
            except KeyError:
                d[mod] = fws.split("\n")

    return d

def get_firmware_package(firmware):
    try:
        fw_packages = COMPONENTDB.get_packages("hardware.firmware")
        unavailable_fw_packages = set(fw_packages).difference(INSTALLDB.list_installed())

        if unavailable_fw_packages:
            ctx.ui.info(inary.util.colorize("The following firmwares are not installed:", "yellow"))
            ctx.ui.info("\n".join(unavailable_fw_packages))

        for module, firmwares in list(get_firmwares().items()):
            ctx.ui.info("\n {} requires the following firmwares:".format(module))
            for fw in firmwares:
                ctx.ui.info("  * {}".format(fw), noln = True)
                try:
                    firmware = inary.api.search_file(fw)[0][0]
                except:
                    pass

                ctx.ui.info(" ({})".format(inary.util.colorize(firmware, 'green') if firmware else \
                        inary.util.colorize("missing", 'red')))
    except:
        raise Error()

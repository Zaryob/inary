# -*- coding:utf-8 -*-
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
#

import inary.trigger
import inary.context as ctx
import inary.errors
import inary.data
import inary.ui
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


def reconfigure(packages=None):
    # start with pending packages
    # configure them in reverse topological order of dependency
    installdb = inary.db.installdb.InstallDB()
    order = packages
    for x in order:
        if installdb.has_package(x):
            pkginfo = installdb.get_package(x)
            ops_Dir = installdb.package_path(x)
            ctx.ui.notify(inary.ui.configuring, package=pkginfo, files=None)
            inary.trigger.Trigger().postinstall(ops_Dir)
            ctx.ui.notify(inary.ui.configured, package=pkginfo, files=None)
        installdb.clear_pending(x)


class ConfigurePending(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Reconfigure pending packages

If SCOM configuration of some packages were not
done at installation time, they are added to a list
of packages waiting to be configured. This command
configures those packages.
""")

    def __init__(self, args):
        super(ConfigurePending, self).__init__(args)

    name = (_("reconfigure"), "rp")

    def options(self):
        group = optparse.OptionGroup(
            self.parser, _("configure-pending options"))
        super(ConfigurePending, self).options(group)
        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)
        reconfigure(self.args)

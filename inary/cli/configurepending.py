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

import optparse

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import os
import inary.util as util
import inary.cli.command as command
import inary.ui
import inary.data
import inary.errors
import inary.context as ctx


def configure_pending(packages=None):
    # start with pending packages
    # configure them in reverse topological order of dependency
    installdb = inary.db.installdb.InstallDB()
    if not packages:
        packages = installdb.list_pending()
    else:
        packages = set(packages).intersection(installdb.list_pending())

    order = inary.data.pgraph.generate_pending_order(packages)
    for x in order:
        if installdb.has_package(x):
            pkginfo = installdb.get_package(x)
            pkg_path = installdb.package_path(x)
            m = inary.data.metadata.MetaData()
            metadata_path = util.join_path(pkg_path, ctx.const.metadata_xml)
            m.read(metadata_path)
            # FIXME: we need a full package info here!
            pkginfo.name = x
            ctx.ui.notify(inary.ui.configuring, package=pkginfo, files=None)

            command=m.package.postopsPostInstall[0]

            if os.system(command) != 0:
                ctx.ui.warning(_('Configuration of \"{}\" package failed.').format(pkginfo.name))
            else:
                installdb.clear_pending(x)
                ctx.ui.notify(inary.ui.configured, package=pkginfo, files=None)

class ConfigurePending(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Configure pending packages

If SCOM configuration of some packages were not
done at installation time, they are added to a list
of packages waiting to be configured. This command
configures those packages.
""")

    def __init__(self, args):
        super(ConfigurePending, self).__init__(args)

    name = ("configure-pending", "cp")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("configure-pending options"))
        super(ConfigurePending, self).options(group)
        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)
        configure_pending(self.args)

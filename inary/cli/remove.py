# -*- coding:utf-8 -*-
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
#

import inary.sysconf as sysconf
import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Remove(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Remove INARY packages

Usage: remove <package1> <package2> ... <packagen>

Remove package(s) from your system. Just give the package names to remove.

You can also specify components instead of package names, which will be
expanded to package names.
""")

    def __init__(self, args):
        super(Remove, self).__init__(args)
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = ("remove", "rm")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("remove options"))
        super(Remove, self).options(group)
        group.add_option("--ignore-sysconf", action="store_true",
                         default=False, help=_("Skip sysconf operations after installation."))
        group.add_option("--force-sysconf", action="store_true",
                         default=False, help=_("Force sysconf operations after installation. Applies all sysconf operations"))
        group.add_option("--purge", action="store_true",
                         default=False, help=_("Removes everything including changed config files of the package."))
        group.add_option("-c", "--component", action="append",
                         default=None, help=_("Remove component's and recursive components' packages."))
        self.parser.add_option_group(group)

    def run(self):
        from inary.operations import remove
        self.init()

        components = ctx.get_option('component')
        if not components and not self.args:
            self.help()
            return

        packages = []
        if components:
            for name in components:
                if self.componentdb.has_component(name):
                    packages.extend(
                        self.componentdb.get_union_packages(
                            name, walk=True))
        packages.extend(self.args)

        remove.remove(packages)

        if not self.options.ignore_sysconf:
            sysconf.proceed(self.options.force_sysconf)

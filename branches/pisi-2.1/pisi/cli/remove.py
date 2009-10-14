# -*- coding:utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.cli.command as command
import pisi.context as ctx
import pisi.api
import pisi.db

class Remove(command.PackageOp):
    __doc__ = _("""Remove PiSi packages

Usage: remove <package1> <package2> ... <packagen>

Remove package(s) from your system. Just give the package names to remove.

You can also specify components instead of package names, which will be
expanded to package names.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Remove, self).__init__(args)
        self.componentdb = pisi.db.componentdb.ComponentDB()

    name = ("remove", "rm")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("remove options"))
        super(Remove, self).options(group)
        group.add_option("--purge", action="store_true",
                     default=False, help=_("Removes everything including changed config files of the package"))
        group.add_option("-c", "--component", action="append",
                               default=None, help=_("Remove component's and recursive components' packages"))
        self.parser.add_option_group(group)

    def run(self):
        self.init()

        components = ctx.get_option('component')
        if not components and not self.args:
            self.help()
            return

        packages = []
        if components:
            for name in components:
                if self.componentdb.has_component(name):
                    packages.extend(self.componentdb.get_union_packages(name, walk=True))
        packages.extend(self.args)

        pisi.api.remove(packages)
        

# -*- coding:utf-8 -*-
#
# Copyright (C)  2017 - 2018,  Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse
import os

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Fetch(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Mirror a repository

Usage: mirror [<package1> <package2> ... <packagen>]

<packagei>: repo name

Downloads the given inary packages to working directory
""")

    def __init__(self, args):
        super(Fetch, self).__init__(args)

    name = ("mirror", "mr")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("mirror options"))

        group.add_option("-o", "--output-dir", action="store", default=os.path.curdir,
                         help=_("Output directory for the mirrored repository"))

        self.parser.add_option_group(group)

    def run(self):
        import inary.fetcher as fetcher
        packages = inary.db.packagedb.PackageDB()
        self.init(database=False, write=False)

        if not self.args:
            self.help()
            return

        full_packages = []

        for repo in self.args:
            full_packages = packages.list_packages(repo)
            for pkgname in full_packages:
                pkg, repo = packages.get_package_repo(pkgname, repo)
                output = os.path.join(
                    ctx.config.options.output_dir, os.path.dirname(pkg.packageURI))
                fetcher.fetch([pkgname], output, repo)

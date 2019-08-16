# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.
#

import optparse

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.db
import inary.data.pgraph as pgraph


class Graph(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Graph package relations

Usage: graph [<package1> <package2> ...]

Write a graph of package relations, tracking dependency and
conflicts relations starting from given packages. By default
shows the package relations among repository packages, and writes
the package in graphviz format to 'pgraph.dot'.
""")

    def __init__(self, args=None):
        super(Graph, self).__init__(args)

    def options(self):

        group = optparse.OptionGroup(self.parser, _("graph options"))

        group.add_option("-r", "--repository", action="store",
                         default=None,
                         help=_("Specify a particular repository."))
        group.add_option("-i", "--installed", action="store_true",
                         default=False,
                         help=_("Graph of installed packages"))
        group.add_option("--ignore-installed", action="store_true",
                         default=False,
                         help=_("Do not show installed packages."))
        group.add_option("-R", "--reverse", action="store_true",
                         default=False,
                         help=_("Draw reverse dependency graph."))
        group.add_option("-o", "--output", action="store",
                         default='pgraph.dot',
                         help=_("Dot output file"))

        self.parser.add_option_group(group)

    name = ("graph", None)

    def run(self):
        self.init(write=False)
        if not ctx.get_option('installed'):
            # Graph from package database
            packagedb = inary.db.packagedb.PackageDB()

            if ctx.get_option('repository'):
                repo = ctx.get_option('repository')
                ctx.ui.info(_('Plotting packages in repository \"{}\"').format(repo))
            else:
                repo = None
                ctx.ui.info(_('Plotting a graph of relations among all repository packages.'))

            if self.args:
                a = self.args
            else:
                a = inary.db.packagedb.PackageDB().list_packages(repo)

        else:
            # Graph from installed packages database
            packagedb = inary.db.installdb.InstallDB()

            if self.args:
                a = self.args
            else:
                # if A is empty, then graph all packages
                ctx.ui.info(_('Plotting a graph of relations among all installed packages.'))
                a = inary.db.installdb.InstallDB().list_installed()

        g = pgraph.package_graph(a, packagedb,
                                 ignore_installed=ctx.get_option('ignore_installed'), reverse=ctx.get_option('reverse'))
        g.write_graphviz(open(ctx.get_option('output'), 'w'))

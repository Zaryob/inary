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

import inary.operations.search as search
import inary.context as ctx
import inary.cli.command as command


class SearchFile(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Search for a file

Usage: search-file <path1> <path2> ... <pathn>

Finds the installed package which contains the specified file.
""")

    def __init__(self, args):
        super(SearchFile, self).__init__(args)

    name = ("search-file", "sf")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("search-file options"))
        group.add_option("-l", "--long", action="store_true",
                         default=False, help=_("Show in long format"))
        group.add_option("-q", "--quiet", action="store_true",
                         default=False, help=_("Show only package name"))
        self.parser.add_option_group(group)

    @staticmethod
    def search_file(path):
        found = search.search_file(path)

        if not found:
            ctx.ui.error(_("Path \"{}\" does not belong to an installed package").format(path))

        for pkg, files in found:
            for pkg_file in files:
                ctx.ui.info(_("Package \"{0}\" has file \"/{1}\"").format(pkg, pkg_file))

    def run(self):

        self.init(database=True, write=False)

        if not self.args:
            self.help()
            return

        # search among existing files
        for path in self.args:
            if not ctx.config.options.quiet:
                ctx.ui.info(_('Searching for \"{}\"').format(path))
            self.search_file(path)

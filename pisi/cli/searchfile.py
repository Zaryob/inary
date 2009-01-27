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

import pisi
import pisi.context as ctx
import pisi.cli.command as command

class SearchFile(command.Command):
    __doc__ = _("""Search for a file

Usage: search-file <path1> <path2> ... <pathn>

Finds the installed package which contains the specified file.
""")
    __metaclass__ = command.autocommand

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

    def search_file(self, path):
        found = pisi.api.search_file(path)
        for pkg, files in found:
            for pkg_file in files:
                ctx.ui.info(_("Package %s has file /%s") % (pkg, pkg_file))

        if not found:
            ctx.ui.error(_("Path '%s' does not belong to an installed package") % path)

    def run(self):

        self.init(database = True, write = False)

        if not self.args:
            self.help()
            return

        # search among existing files
        for path in self.args:
            if not ctx.config.options.quiet:
                ctx.ui.info(_('Searching for %s') % path)
            self.search_file(path)

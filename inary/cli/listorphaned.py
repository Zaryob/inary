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
import inary.util as util


class ListOrphaned(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List orphaned packages

Usage: list-orphaned

Lists packages installed as dependency, but no longer needed by any other installed package.
""")

    def __init__(self, args):
        super(ListOrphaned, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()

    name = ("list-orphaned", "lo")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-orphaned options"))
        group.add_option("-a", "--all", action="store_true",
                         default=False, help=_("Show all packages without reverse dependencies."))
        group.add_option("-x", "--exclude", action="append",
                         default=None, help=_("Ignore packages and components whose basenames match pattern."))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database=True, write=False)
        orphaned = self.installdb.get_no_rev_deps() if self.options.all else self.installdb.get_orphaned()

        if self.options.exclude:
            orphaned = inary.blacklist.exclude(orphaned, ctx.get_option('exclude'))

        if orphaned:
            ctx.ui.info(_("Orphaned packages:"))
            ctx.ui.info(util.format_by_columns(sorted(orphaned)))
        else:
            ctx.ui.info(_("No orphaned packages."))

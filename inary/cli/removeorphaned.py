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

import inary.cli.command as command
import inary.context as ctx
from inary.operations import remove
import inary.db


class RemoveOrphaned(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Remove orphaned packages

Usage: remove-orphaned

Remove all orphaned packages from the system.
""")

    def __init__(self, args):
        super(RemoveOrphaned, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()

    name = ("remove-orphaned", "ro")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("remove-orphaned options"))

        super(RemoveOrphaned, self).options(group)
        group.add_option("-x", "--exclude", action="append",
                         default=None, help=_(
                "When removing orphaned, ignore packages and components whose basenames match pattern."))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)
        orphaned = self.installdb.get_orphaned()
        if ctx.get_option('exclude'):
            orphaned = inary.blacklist.exclude(orphaned, ctx.get_option('exclude'))

        remove.remove(orphaned)

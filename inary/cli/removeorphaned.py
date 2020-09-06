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
import inary.blacklist
import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class RemoveOrphaned(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Remove orphaned packages

Usage: remove-orphaned

Remove all orphaned packages from the system.
""")

    def __init__(self, args):
        super(RemoveOrphaned, self).__init__(args)

    name = ("remove-orphaned", "ro")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("remove-orphaned options"))

        super(RemoveOrphaned, self).options(group)
        group.add_option("-x", "--exclude", action="append",
                         default=None, help=_(
                             "When removing orphaned, ignore packages and components whose basenames match pattern."))
        group.add_option("--ignore-sysconf", action="store_true",
                         default=False, help=_("Skip sysconf operations after installation."))
        group.add_option("--force-sysconf", action="store_true",
                         default=False, help=_("Force sysconf operations after installation. Applies all sysconf operations"))

        self.parser.add_option_group(group)

    def run(self):
        from inary.operations import remove
        self.init()
        orphaned = [0]
        first = True
        while len(orphaned) > 0:
            orphaned = inary.db.installdb.InstallDB().get_orphaned()
            if ctx.get_option('exclude'):
                orphaned = inary.blacklist.exclude(
                    orphaned, ctx.get_option('exclude'))

            if len(orphaned) > 0:
                remove.remove(orphaned, confirm=first)
                first = False

        if not self.options.ignore_sysconf:
            sysconf.proceed(self.options.force_sysconf)

# -*- coding:utf-8 -*-
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

import inary.sysconf as sc
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class runsysconf(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Run sysconf trigger""")

    def __init__(self, args):
        super(runsysconf, self).__init__(args)

    name = (_("sysconf"), "sc")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("sysconf options"))
        group.add_option("-f", "--force", action="store_true",
                         default=False, help=_("Run force sysconf"))

    def run(self):
        sc.proceed(self.options.force)

# -*- coding:utf-8 -*-
#
# Copyright (C) 2016  -  2017,  Suleyman POYRAZ (Zaryob)
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
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.atomicoperations
import inary.cli.command as command

class ConfigurePending(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Configure pending packages

If SCOM configuration of some packages were not
done at installation time, they are added to a list
of packages waiting to be configured. This command
configures those packages.
""")

    def __init__(self, args):
        super(ConfigurePending, self).__init__(args)

    name = ("configure-pending", "cp")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("configure-pending options"))
        super(ConfigurePending, self).options(group)
        self.parser.add_option_group(group)

    def run(self):

        self.init()
        inary.atomicoperations.configure_pending(self.args)

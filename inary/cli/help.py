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

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli
import inary.cli.command as command
import inary.context as ctx


class Help(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Prints help for given commands

Usage: help [ <command1> <command2> ... <commandn> ]

If run without parameters, it prints the general help.""")

    def __init__(self, args=None):
        super(Help, self).__init__(args)

    name = ("help", "?")

    def run(self):

        if not self.args:
            self.parser.set_usage(usage_text)
            inary.cli.printu(self.parser.format_help())
            return

        self.init(database=False, write=False)

        for arg in self.args:
            obj = command.Command.get_command(arg, True)
            obj.help()
            ctx.ui.info('')


usage_text1 = _("""%prog [options] <command> [arguments]

where <command> is one of:

""")

usage_text2 = _("""
Use \"%prog help <command>\" for help on a specific command.
""")

usage_text = (usage_text1 + command.Command.commands_string() + usage_text2)

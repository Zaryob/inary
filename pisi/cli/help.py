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

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.cli
import pisi.cli.command as command
import pisi.context as ctx

class Help(command.Command):
    __doc__ = _("""Prints help for given commands

Usage: help [ <command1> <command2> ... <commandn> ]

If run without parameters, it prints the general help.""")

    __metaclass__ = command.autocommand

    def __init__(self, args = None):
        super(Help, self).__init__(args)

    name = ("help", "?")

    def run(self):

        if not self.args:
            self.parser.set_usage(usage_text)
            pisi.cli.printu(self.parser.format_help())
            return

        self.init(database = False, write = False)

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

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
import pisi.api
import pisi.db
import pisi.context as ctx
import pisi.cli.command as command

class History(command.Command):
    """History of pisi operations

Usage: history

Lists previous operations."""

    __metaclass__ = command.autocommand

    def __init__(self, args=None):
        super(History, self).__init__(args)
        self.historydb = pisi.db.historydb.HistoryDB()

    name = ("history", "hs")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("history options"))
        self.add_options(group)
        self.parser.add_option_group(group)

    def add_options(self, group):
        group.add_option("-l", "--last", action="store", type="int", default=0,
                         help=_("Output only the last n operations"))

    def run(self):
        self.init(database = False, write = False)
        for operation in self.historydb.latest_operations(ctx.get_option('last')):
            print "Operation: %s" % operation.type
            print "Date: %s %s" % (operation.date, operation.time)
            print
            for pkg in operation.packages:
                print "    *", pkg
            print

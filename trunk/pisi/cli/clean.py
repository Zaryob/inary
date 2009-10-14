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

import pisi.cli.command as command

class Clean(command.Command):
    __doc__ = _("""Clean stale locks

Usage: clean

PiSi uses filesystem locks for managing database access.
This command deletes unused locks from the database directory.""")

    __metaclass__ = command.autocommand

    def __init__(self, args=None):
        super(Clean, self).__init__(args)

    name = ("clean", None)

    def run(self):
        self.init()
        

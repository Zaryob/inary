# -*- coding:utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2017 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command

class Clean(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Clean stale locks

Usage: clean

INARY uses filesystem locks for managing database access.
This command deletes unused locks from the database directory.""")

    def __init__(self, args=None):
        super(Clean, self).__init__(args)

    name = ("clean", None)

    def run(self):
        self.init()

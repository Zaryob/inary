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

import pisi
import pisi.api
import pisi.cli.command as command

class History(command.Command):
    """History of pisi operations

Usage: history

Lists previous operations."""

    __metaclass__ = command.autocommand

    def __init__(self, args=None):
        super(History, self).__init__(args)

    name = ("history", "hs")

    def run(self):
        pass

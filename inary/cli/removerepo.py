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

import inary.cli.command as command
import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class RemoveRepo(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Remove repositories

Usage: remove-repo <repo1> <repo2> ... <repon>

Remove all repository information from the system.
""")

    def __init__(self, args):
        super(RemoveRepo, self).__init__(args)

    name = ("remove-repo", "rr")

    def run(self):
        from inary.operations import repository
        if len(self.args) >= 1:
            self.init()
            for repo in self.args:
                repository.remove_repo(repo)
        else:
            self.help()
            return

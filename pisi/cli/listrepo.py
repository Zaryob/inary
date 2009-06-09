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
import pisi.context as ctx
import pisi.db

class ListRepo(command.Command):
    __doc__ = _("""List repositories

Usage: list-repo

Lists currently tracked repositories.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListRepo, self).__init__(args)
        self.repodb = pisi.db.repodb.RepoDB()

    name = ("list-repo", "lr")

    def run(self):

        self.init(database = True, write = False)
        for repo in self.repodb.list_repos():
            ctx.ui.info(repo)
            #FIXME: repodb.get_repo(repo).indexuri.get_uri()??? ick!
            print '  ', self.repodb.get_repo(repo).indexuri.get_uri()

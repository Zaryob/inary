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

import inary.cli.command as command
import inary.context as ctx
import inary.db


class ListRepo(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List repositories

Usage: list-repo

Lists currently tracked repositories.
""")

    def __init__(self, args):
        super(ListRepo, self).__init__(args)
        self.repodb = inary.db.repodb.RepoDB()

    name = ("list-repo", "lr")

    def run(self):

        self.init(database=True, write=False)
        for repo in self.repodb.list_repos(only_active=False):
            active = _("active") if self.repodb.repo_active(repo) else _("inactive")
            if active == _("active"):
                ctx.ui.info(_("{0} [{1}]").format(repo, active), color='green')
            else:
                ctx.ui.info(_("{0} [{1}]").format(repo, active), color='red')
            print('  ', self.repodb.get_repo_url(repo))

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

import pisi.cli.command as command
import pisi.context as ctx
import pisi.api

class UpdateRepo(command.Command):
    __doc__ = _("""Update repository databases

Usage: update-repo [<repo1> <repo2> ... <repon>]

<repoi>: repository name

Synchronizes the PiSi databases with the current repository.
If no repository is given, all repositories are updated.
""")
    __metaclass__ = command.autocommand

    def __init__(self,args):
        super(UpdateRepo, self).__init__(args)

    name = ("update-repo", "ur")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("update-repo options"))

        group.add_option("-f", "--force", action="store_true",
                               default=False,
                               help=_("Update database in any case"))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database = True)

        if self.args:
            repos = self.args
        else:
            repos = pisi.api.list_repos()

        pisi.api.update_repos(repos, ctx.get_option('force'))

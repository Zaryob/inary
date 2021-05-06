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

# Standard Python Modules
import optparse

# Inary Modules
import inary.db
import inary.errors
import inary.context as ctx
import inary.cli.command as command
import inary.operations.repository as repository

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class AddRepo(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Add a repository

Usage: add-repo <repo> <indexuri>

<repo>: name of repository to add
<indexuri>: URI of index file

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
""")

    def __init__(self, args):
        super(AddRepo, self).__init__(args)
        self.repodb = inary.db.repodb.RepoDB()

    name = ("add-repo", "ar")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("add-repo options"))
        group.add_option("--ignore-check", action="store_true", default=False,
                         help=_("Ignore repository distribution check"))
        group.add_option("--no-fetch", action="store_true", default=False,
                         help=_("Does not fetch repository index and does not check distribution match"))
        group.add_option("--at", action="store",
                         type="int", default=None,
                         help=_("Add repository at given position (0 is first)"))
        self.parser.add_option_group(group)

    @staticmethod
    def warn_and_remove(message, repo):
        ctx.ui.warning(message)
        repository.remove_repo(repo)

    def run(self):
        if len(self.args) == 2:
            self.init()
            name, indexuri = self.args

            if indexuri.endswith(".xml.xz") or indexuri.endswith(".xml"):
                repository.add_repo(name, indexuri, ctx.get_option('at'))
            else:
                raise Exception(
                    _("Extension of repository URI must be \".xml.xz\" or \".xml\"."))

        else:
            self.help()
            return

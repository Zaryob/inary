# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.operations.repository as repository
import inary.cli.command as command
import inary.context as ctx
import inary.db
import inary.errors
import inary.misc.epoch2string as e2s


class AddRepo(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Add a repository

Usage: add-repo <repo-name> <indexuri>
       add-repo <indexuri>

<repo-name>: It is the optional parameter that using to define repository name.
             Unless defined, random data will be used as repository name.
<indexuri>: URI of index file

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
""")

    def __init__(self, args):
        super(AddRepo, self).__init__(args)
        self.repodb = inary.db.repodb.RepoDB()

    name = (_("add-repo"), "ar")

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
        name, indexuri = None, None
        if len(self.args) == 1:
            #We need time based random name.
            name = e2s.nextString()
            indexuri = self.args[0]

        elif len(self.args) == 2:
            name, indexuri = self.args

            if ctx.get_option('no_fetch'):
                if not ctx.ui.confirm(_('Add {} repository without updating the database?\nBy confirming '
                                        'this you are also adding the repository to your system without '
                                        'checking the distribution of the repository.\n'
                                        'Do you want to continue?').format(name)):
                    return
            if indexuri.endswith(".xml.xz") or indexuri.endswith(".xml"):
                repository.add_repo(name, indexuri, ctx.get_option('at'))
            else:
                raise Exception(_("Extension of URI must be \".xml.xz\" or \".xml\"  "))


        else:
            self.help()
            return

        self.init()
        ctx.ui.debug(_("The repository: {} \tIndex URI: {} "))


        if ctx.get_option('no_fetch'):
            if not ctx.ui.confirm(_('Add {} repository without updating the database?\nBy confirming '
                                'this you are also adding the repository to your system without '
                                'checking the distribution of the repository.\n'
                                'Do you want to continue?').format(name)):
                return

        repository.add_repo(name, indexuri, ctx.get_option('at'))

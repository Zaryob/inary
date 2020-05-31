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
            self.just_add = False

            if ctx.get_option('no_fetch'):
                if ctx.ui.confirm(_('Add \"{}\" repository without updating the database?\nBy confirming '
                                    'this you are also adding the repository to your system without '
                                    'checking the distribution of the repository.\n'
                                    'Would you like to continue?').format(name)):
                    self.just_add = True

            if indexuri.endswith(".xml.xz") or indexuri.endswith(".xml"):
                repository.add_repo(name, indexuri, ctx.get_option('at'))
                if not self.just_add:
                    try:
                        repository.update_repos([name])
                    except (inary.errors.Error, IOError) as e:
                        ctx.ui.info(
                            _("Error: {0} repository could not be reached: \n{1}").format(
                                name, e), color="red")
                        self.warn_and_remove(
                            _("Removing {0} from system.").format(name), name)
                else:
                    ctx.ui.warning(
                        _("Couldn't trust \"{0}\" repository. It is deactivated.").format(name))
                    repository.set_repo_activity(name, False)

            else:
                raise Exception(
                    _("Extension of repository URI must be \".xml.xz\" or \".xml\"."))

        else:
            self.help()
            return

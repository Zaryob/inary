# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C)  2017 - 2018,  Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ListNewest(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List newest packages in the repositories

Usage: list-newest [ <repo1> <repo2> ... repon ]

Gives a list of INARY newly published packages in the specified
repositories. If no repository is specified, we list the new
packages from all repositories.
""")

    def __init__(self, args):
        super(ListNewest, self).__init__(args)
        self.componentdb = inary.db.componentdb.ComponentDB()
        self.packagedb = inary.db.packagedb.PackageDB()
        self.historydb = inary.db.historydb.HistoryDB()

    name = ("list-newest", "ln")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-newest options"))
        group.add_option("-s", "--since", action="store",
                         default=None,
                         help=_("List new packages added to repository after this given date formatted as yyyy-mm-dd."))
        group.add_option("-l", "--last", action="store",
                         default=None,
                         help=_("List new packages added to repository after last nth previous repository update."))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database=True, write=False)
        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in inary.db.repodb.RepoDB().list_repos(only_active=True):
                self.print_packages(repo)

    def print_packages(self, repo):
        if ctx.config.get_option('since'):
            since = ctx.config.get_option('since')
        elif ctx.config.get_option('last'):
            since = self.historydb.get_last_repo_update(
                int(ctx.config.get_option('last')))
        else:
            since = None
        l = self.packagedb.list_newest(repo, since, self.historydb)
        if not l:
            return
        if since:
            ctx.ui.info(
                _("Packages added to \'{0}\' since \"{1}\":\n").format(
                    repo, since))
        else:
            ctx.ui.info(_("Packages added to \'{}\':").format(repo))

        # maxlen is defined dynamically from the longest package name (#9021)
        maxlen = max([len(_p) for _p in l])

        l.sort()
        for p in l:
            pkgsum = self.packagedb.get_summary(p)
            lenp = len(p)
            p += ' ' * max(0, maxlen - lenp)
            ctx.ui.info('{0} - {1} '.format(p, str(pkgsum)))

        print()

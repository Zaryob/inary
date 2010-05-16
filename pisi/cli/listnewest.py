# -*- coding:utf-8 -*-
#
# Copyright (C) 2009, TUBITAK/UEKAE
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
import pisi.db

class ListNewest(command.Command):
    __doc__ = _("""List newest packages in the repositories

Usage: list-newest [ <repo1> <repo2> ... repon ]

Gives a list of PiSi newly published packages in the specified
repositories. If no repository is specified, we list the new
packages from all repositories.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListNewest, self).__init__(args)
        self.componentdb = pisi.db.componentdb.ComponentDB()
        self.packagedb = pisi.db.packagedb.PackageDB()

    name = ("list-newest", "ln")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-newest options"))
        group.add_option("-s", "--since", action="store",
                               default=None, help=_("List new packages added to repository after this given date formatted as yyyy-mm-dd"))
        group.add_option("-l", "--last", action="store",
                               default=None, help=_("List new packages added to repository after last nth previous repository update"))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database = True, write = False)

        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in pisi.api.list_repos():
                self.print_packages(repo)

    def print_packages(self, repo):
        if ctx.config.get_option('since'):
            since = ctx.config.get_option('since')
        elif ctx.config.get_option('last'):
            since = pisi.db.historydb.HistoryDB().get_last_repo_update(int(ctx.config.get_option('last')))
        else:
            since = None

        l = pisi.api.list_newest(repo, since)
        if not l:
            return

        if since:
            ctx.ui.info(_("Packages added to %s since %s:\n") % (repo, since))
        else:
            ctx.ui.info(_("Packages added to %s:") % (repo))

        # maxlen is defined dynamically from the longest package name (#9021)
        maxlen = max([len(_p) for _p in l])

        l.sort()
        for p in l:
            package = self.packagedb.get_package(p, repo)
            lenp = len(p)
            p = p + ' ' * max(0, maxlen - lenp)
            ctx.ui.info('%s - %s ' % (p, unicode(package.summary)))

        print


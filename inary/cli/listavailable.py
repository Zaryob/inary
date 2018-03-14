# -*- coding:utf-8 -*-
#
# Copyright (C) 2016  -  2017,  Suleyman POYRAZ (Zaryob)
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
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.util as util
import inary.atomicoperations
import inary.db
import inary.operations.op_wrappers as op_wrappers

class ListAvailable(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List available packages in the repositories

Usage: list-available [ <repo1> <repo2> ... repon ]

Gives a brief list of INARY packages published in the specified
repositories. If no repository is specified, we list packages in
all repositories.
""")

    def __init__(self, args):
        super(ListAvailable, self).__init__(args)
        self.componentdb = inary.db.componentdb.ComponentDB()
        self.packagedb = inary.db.packagedb.PackageDB()

    name = ("list-available", "la")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-available options"))
        group.add_option("-l", "--long", action="store_true",
                               default=False, help=_("Show in long format"))
        group.add_option("-c", "--component", action="store",
                               default=None, help=_("List available packages under given component"))
        group.add_option("-U", "--uninstalled", action="store_true",
                               default=False, help=_("Show uninstalled packages only"))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database = True, write = False)

        if not (ctx.get_option('no_color') or ctx.config.get_option('uninstalled')):
            ctx.ui.info(util.colorize(_('Installed packages are shown in this color'), 'green'))

        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in op_wrappers.list_repos():
                ctx.ui.info(_("Repository : {}\n").format(str(repo)))
                self.print_packages(repo)

    def print_packages(self, repo):

        component = ctx.get_option('component')
        if component:
            try:
                l = self.componentdb.get_packages(component, repo=repo, walk=True)
            except Exception as e:
                return
        else:
            l = op_wrappers.list_available(repo)

        installed_list = op_wrappers.list_installed()

        # maxlen is defined dynamically from the longest package name (#9021)
        if l:
            maxlen = max([len(_p) for _p in l])

        l.sort()
        for p in l:
            if ctx.config.get_option('uninstalled') and p in installed_list:
                continue

            package = self.packagedb.get_package(p, repo)

            if p in installed_list:
                package.name = util.colorize(package.name, 'green')
            else:
                package.name = util.colorize(package.name, 'brightwhite')

            if self.options.long:
                ctx.ui.info(str(package)+'\n')
            else:
                package.name += ' ' * max(0, maxlen - len(p))
                ctx.ui.info('{0} - {1} '.format(package.name, str(package.summary)))

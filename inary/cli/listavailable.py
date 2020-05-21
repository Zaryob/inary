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

import inary.db
import inary.util as util
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


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
        group.add_option("-n", "--name-only", action="store_true",
                         default=False, help=_("Write only names."))
        # group.add_option("-l", "--long", action="store_true",
        #                 default=False, help=_("Show in long format"))
        group.add_option("-c", "--component", action="store",
                         default=None, help=_("List available packages under given component"))
        group.add_option("-U", "--uninstalled", action="store_true",
                         default=False, help=_("Show uninstalled packages only"))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database=True, write=False)

        if not (ctx.get_option('no_color')
                or ctx.config.get_option('uninstalled')):
            ctx.ui.info(
                _('Installed packages are shown in this color.'),
                color='green')

        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in inary.db.repodb.RepoDB().list_repos(only_active=True):
                ctx.ui.info(
                    _("\n Repository : \"{}\"\n").format(
                        str(repo)), color="blue")
                self.print_packages(repo)

    def print_packages(self, repo):

        component = ctx.get_option('component')
        if component:
            try:
                l = self.componentdb.get_packages(
                    component, repo=repo, walk=True)
            except BaseException:
                return
        else:
            l = self.packagedb.list_packages(repo)

        installed_list = inary.db.installdb.InstallDB().list_installed()

        # maxlen is defined dynamically from the longest package name (#9021)
        if l:
            maxlen = max([len(_p) for _p in l])

        l.sort()
        for p in l:
            if ctx.config.get_option('uninstalled') and p in installed_list:
                continue

            pkgname = ""
            pkgsum = self.packagedb.get_summary(p, repo)

            if p in installed_list:
                pkgname = util.colorize(p, 'green')
            else:
                pkgname = util.colorize(p, 'brightwhite')

            # if self.options.long:
            #    package = self.packagedb.get_package(p)
            #    inst_info = self.packagedb.get_info(p)
            #    ctx.ui.info(str(package))
            #    ctx.ui.info(str(inst_info))

            if self.options.name_only:
                ctx.ui.info(str(pkgname))
            else:
                pkgname += ' ' * max(0, maxlen - len(p))
                ctx.ui.info('{0} - {1} '.format(pkgname, str(pkgsum)))

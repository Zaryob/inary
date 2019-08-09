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

import inary.cli.command as command
import inary.context as ctx
import inary.db
import sys


class ListInstalled(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Print the list of all installed packages

Usage: list-installed
""")

    def __init__(self, args):
        super(ListInstalled, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = (_("list-installed"), "li")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-installed options"))

        group.add_option("-b", "--with-build-host",
                         action="store",
                         default=None,
                         help=_("Only list the installed packages built "
                                "by the given host"))
        group.add_option("-l", "--long", action="store_true",
                         default=False, help=_("Show in long format"))
        group.add_option("-c", "--component", action="store",
                         default=None, help=_("List installed packages under given component"))
        group.add_option("-i", "--install-info", action="store_true",
                         default=False, help=_("Show detailed install info"))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)

        build_host = ctx.get_option("with_build_host")
        if build_host is None:
            installed = self.installdb.list_installed()
        else:
            installed = self.installdb.list_installed_with_build_host(build_host)

        component = ctx.get_option('component')
        if component:
            component_pkgs = self.componentdb.get_union_packages(component, walk=True)
            installed = list(set(installed) & set(component_pkgs))

        installed.sort()

        # Resize the first column according to the longest package name
        if installed:
            maxlen = max([len(_p) for _p in installed])

        if self.options.install_info:
            ctx.ui.info(_('Package Name          |St|        Version|  Rel.|  Distro|             Date'))
            sys.stdout.write('===========================================================================\n')
        for pkg in installed:
            package = self.installdb.get_package(pkg)
            inst_info = self.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(str(package))
                ctx.ui.info(str(inst_info))
            elif self.options.install_info:
                ctx.ui.info('%-20s  ' % package.name, color='white', noln=True)
                ctx.ui.info('|%s' % inst_info.one_liner())
            else:
                package.name += ' ' * (maxlen - len(package.name))
                ctx.ui.info('{} '.format(package.name), color='white', noln=True)
                ctx.ui.info('- {}'.format(str(package.summary)))

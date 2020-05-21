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

import sys
import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ListInstalled(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Print the list of all installed packages

Usage: list-installed
""")

    def __init__(self, args):
        super(ListInstalled, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = ("list-installed", "li")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-installed options"))

        group.add_option("-b", "--with-build-host",
                         action="store",
                         default=None,
                         help=_("Only list the installed packages built "
                                "by the given host."))
        group.add_option("-l", "--long", action="store_true",
                         default=False, help=_("Show in long format"))
        group.add_option("-n", "--name-only", action="store_true",
                         default=False, help=_("Write only names."))
        group.add_option("-c", "--component", action="store",
                         default=None, help=_("List installed packages under given component."))
        group.add_option("-i", "--install-info", action="store_true",
                         default=False, help=_("Show detailed install info."))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)

        build_host = ctx.get_option("with_build_host")
        if build_host is None:
            installed = self.installdb.list_installed()
        else:
            installed = self.installdb.list_installed_with_build_host(
                build_host)

        component = ctx.get_option('component')
        if component:
            component_pkgs = self.componentdb.get_union_packages(
                component, walk=True)
            installed = list(set(installed) & set(component_pkgs))

        installed.sort()

        # Resize the first column according to the longest package name
        if installed:
            maxlen = max([len(_p) for _p in installed])

        if self.options.install_info:
            ctx.ui.info(
                _('Package Name          |St|        Version|  Rel.|  Distro|             Date'))
            sys.stdout.write(
                '===========================================================================\n')

        if self.options.long:
            for pkg in installed:
                inst_info = self.installdb.get_info(pkg)
                ctx.ui.info(str(pkg))
                ctx.ui.info(str(inst_info))

        elif self.options.install_info:
            for pkg in installed:
                inst_info = self.installdb.get_info(pkg)
                ctx.ui.info('%-20s  ' % pkg, color='white', noln=True)
                ctx.ui.info('|%s' % inst_info.one_liner())

        elif self.options.name_only:
            for pkg in installed:
                ctx.ui.info(pkg, color='white')

        else:
            for pkg in installed:
                pkgname = pkg
                psum = self.installdb.get_summary(pkg)
                pkgname += ' ' * (maxlen - len(pkg))
                ctx.ui.info('{} '.format(pkgname), color='white', noln=True)
                ctx.ui.info('- {}'.format(str(psum)))

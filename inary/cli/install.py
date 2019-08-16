# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.
#

import optparse

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
from inary.operations import install
import inary.db


class Install(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Install INARY packages

Usage: install <package1> <package2> ... <packagen>

You may use filenames, URI's or package names for packages. If you have
specified a package name, it should exist in a specified repository.

You can also specify components instead of package names, which will be
expanded to package names.
""")

    def __init__(self, args):
        super(Install, self).__init__(args)
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = "install", "it"

    def options(self):
        group = optparse.OptionGroup(self.parser, _("install options"))

        super(Install, self).options(group)

        group.add_option("--reinstall", action="store_true",
                         default=False, help=_("Reinstall already installed packages."))
        group.add_option("--ignore-check", action="store_true",
                         default=False, help=_("Skip distribution release and architecture check."))
        group.add_option("--ignore-file-conflicts", action="store_true",
                         default=False, help=_("Ignore file conflicts"))
        group.add_option("--ignore-package-conflicts", action="store_true",
                         default=False, help=_("Ignore package conflicts"))
        group.add_option("-c", "--component", action="append",
                         default=None, help=_("Install component's and recursive components' packages."))
        group.add_option("-r", "--repository", action="store",
                         type="string", default=None, help=_('Name of the component\'s repository.'))
        group.add_option("-f", "--fetch-only", action="store_true",
                         default=False, help=_("Fetch upgrades but do not install."))
        group.add_option("-x", "--exclude", action="append",
                         default=None, help=_(
                "When installing packages, ignore packages and components whose basenames match pattern."))
        group.add_option("--exclude-from", action="store",
                         default=None,
                         help=_("When installing packages, ignore packages "
                                "and components whose basenames match "
                                "any pattern contained in file."))
        group.add_option("-s", "--store-lib-info", action="store_true",
                         default=False,
                         help=_("Store previous libraries info when package is updating to newer version."))
        self.parser.add_option_group(group)

    def run(self):

        if self.options.fetch_only:
            self.init(database=True, write=False)
        else:
            self.init()

        components = ctx.get_option('component')
        if not components and not self.args:
            self.help()
            return

        packages = []
        if components:
            for name in components:
                if self.componentdb.has_component(name):
                    repository = ctx.get_option('repository')
                    if repository:
                        packages.extend(self.componentdb.get_packages(name, walk=True, repo=repository))
                    else:
                        packages.extend(self.componentdb.get_union_packages(name, walk=True))
                else:
                    ctx.ui.info(_('There is no component named  as \"{}\"').format(name))

        packages.extend(self.args)

        if ctx.get_option('exclude_from'):
            packages = inary.blacklist.exclude_from(packages, ctx.get_option('exclude_from'))

        if ctx.get_option('exclude'):
            packages = inary.blacklist.exclude(packages, ctx.get_option('exclude'))

        reinstall = bool(packages) and packages[0].endswith(ctx.const.package_suffix)
        install.install(packages, ctx.get_option('reinstall') or reinstall)

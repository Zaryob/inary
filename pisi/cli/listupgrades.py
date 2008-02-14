# -*- coding:utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import optparse

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.cli.command as command
import pisi.context as ctx
import pisi.api
import pisi.db

class ListUpgrades(command.Command):
    """List packages to be upgraded

Usage: list-upgrades

Lists the packages that will be upgraded.
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListUpgrades, self).__init__(args)
        self.componentdb = pisi.db.componentdb.ComponentDB()
        self.installdb = pisi.db.installdb.InstallDB()

    name = ("list-upgrades", "lu")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("list-upgrades options"))
        group.add_option("--ignore-build-no", action="store_true",
                               default=False,
                               help=_("Do not take build no into account."))
        group.add_option("-l", "--long", action="store_true",
                               default=False, help=_("Show in long format"))
        group.add_option("-c", "--component", action="store",
                               default=None, help=_("List upgradable packages under given component"))
        group.add_option("-i", "--install-info", action="store_true",
                               default=False, help=_("Show detailed install info"))
        self.parser.add_option_group(group)

    def exclude_from(self, packages, exfrom):
        patterns = []
        if os.path.exists(exfrom):
            for line in open(exfrom, "r").readlines():
                if not line.startswith('#') and not line == '\n':
                    patterns.append(line.strip())
            if patterns:
                return self.exclude(packages, patterns)

        return packages

    def exclude(self, packages, patterns):
        from sets import Set as set
        import fnmatch

        packages = set(packages)
        for pattern in patterns:
            # match pattern in package names
            match = fnmatch.filter(packages, pattern)
            packages = packages - set(match)

            if not match:
                # match pattern in component names
                for compare in fnmatch.filter(self.componentdb.list_components(), pattern):
                    packages = packages - set(self.componentdb.get_union_packages(compare, walk=True))

        return list(packages)

    def run(self):
        self.init(database = True, write = False)
        upgradable_pkgs = pisi.api.list_upgradable()

        component = ctx.get_option('component')
        if component:
            #FIXME: PiSi api is insufficient to do this
            from sets import Set as set
            component_pkgs = self.componentdb.get_union_packages(component, walk=True)
            upgradable_pkgs = list(set(upgradable_pkgs) & set(component_pkgs))

        if os.path.exists(ctx.const.blacklist):
            upgradable_pkgs = self.exclude_from(upgradable_pkgs, ctx.const.blacklist)

        if not upgradable_pkgs:
            ctx.ui.info(_('No packages to upgrade.'))

        upgradable_pkgs.sort()
        if self.options.install_info:
            ctx.ui.info(_('Package Name     |St|   Version|  Rel.| Build|  Distro|             Date'))
            print         '========================================================================'
        for pkg in upgradable_pkgs:
            package = self.installdb.get_package(pkg)
            inst_info = self.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(package)
                print inst_info
            elif self.options.install_info:
                ctx.ui.info('%-15s | %s ' % (package.name, inst_info.one_liner()))
            else:
                ctx.ui.info('%15s - %s ' % (package.name, package.summary))

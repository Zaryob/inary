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

import optparse

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.api
import pisi.cli.command as command
import pisi.context as ctx
import pisi.db

class Check(command.Command):
    __doc__ = _("""Verify installation

Usage: check [<package1> <package2> ... <packagen>]

<packagei>: package name

A cryptographic checksum is stored for each installed
file. Check command uses the checksums to verify a package.
Just give the names of packages.

If no packages are given, checks all installed packages.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Check, self).__init__(args)
        self.installdb = pisi.db.installdb.InstallDB()
        self.componentdb = pisi.db.componentdb.ComponentDB()

    name = ("check", None)

    def options(self):
        group = optparse.OptionGroup(self.parser, _("check options"))
        group.add_option("-c", "--component", action="store",
                              default=None, help=_("Check installed packages under given component"))
        group.add_option("--config", action="store_true",
                     default=False, help=_("Checks only changed config files of the packages"))
        self.parser.add_option_group(group)

    def run(self):
        self.init(database = True, write = False)

        component = ctx.get_option('component')
        if component:
            #FIXME: pisi api is insufficient to do this
            installed = pisi.api.list_installed()
            component_pkgs = self.componentdb.get_union_packages(component, walk=True)
            pkgs = list(set(installed) & set(component_pkgs))
        elif self.args:
            pkgs = self.args
        else:
            ctx.ui.info(_('Checking all installed packages'))
            pkgs = pisi.api.list_installed()

        check_config = ctx.get_option('config')
        for pkg in pkgs:
            ctx.ui.info(_('* Checking %s... ') % pkg, noln=True)
            if self.installdb.has_package(pkg):
                check_results = pisi.api.check(pkg, check_config)
                corrupted = check_results['missing'] or check_results['corrupted']
                if corrupted:
                    if check_config:
                        ctx.ui.info(_('\nPackage %s has changed config files.') % pkg)
                    else:
                        ctx.ui.info(_('\nPackage %s is corrupt.') % pkg)
                else:
                    ctx.ui.info(_("OK"), verbose=False)
            else:
                ctx.ui.info(_('Package %s not installed') % pkg)

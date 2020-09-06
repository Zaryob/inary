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

import os
import sys
import inary.db
import inary.util as util
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class CheckRelation(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Check packages and system relations

Usage: check-relation
""")

    def __init__(self, args):
        super(CheckRelation, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = ("check-relation", "cr")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-installed options"))

        group.add_option("-f", "--force", action="store_true",
                         default=False, help=_("Deep scan mode"))

        self.parser.add_option_group(group)

    def fix_reinstall(self, need_reinstall):
        need_reinstall = util.unique_list(need_reinstall)
        if len(need_reinstall) > 0:
            sys.stderr.write(
                _("This packages broken and need to reinstall.")+"\n\n")
            for pkg in need_reinstall:
                sys.stderr.write("{} ".format(pkg))
                from inary.operations import install
            ctx.set_option("ignore_dependency", True)
            install.install(need_reinstall, reinstall=True)
            sys.stderr.write("\n")

    def run(self):
        self.init(database=True, write=False)
        installed = self.installdb.list_installed()
        component = ctx.get_option('component')
        if component:
            component_pkgs = self.componentdb.get_union_packages(
                component, walk=True)
            installed = list(set(installed) & set(component_pkgs))

        installed.sort()
        need_reinstall = []

        for pkg in installed:
            for p in self.installdb.get_package(pkg).runtimeDependencies():
                sys.stderr.write("\x1b[K"+_("Checking: {}").format(p)+"\r")
                if not self.installdb.has_package(str(p.package)):
                    need_reinstall.append(p.package)
                    sys.stderr.write(
                        _("Missing: - {}").format(p.package)+"\n")
        self.fix_reinstall(need_reinstall)

        if self.options.force:
            for pkg in installed:
                pkgname = pkg
                files = self.installdb.get_files(pkg)
                sys.stderr.write("\x1b[K"+_("Checking: {}").format(pkg)+"\r")
                for f in files.list:
                    if not os.path.exists("/"+f.path):
                        need_reinstall.append(pkg)
                        sys.stderr.write(
                            _("Missing: /{} - {}").format(f.path, pkg)+"\n")
            self.fix_reinstall(need_reinstall)

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
    __doc__ = _("""Check packages integration

Usage: check-integration
""")

    def __init__(self, args):
        super(CheckRelation, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = ("check-integration", "ci")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-installed options"))

        group.add_option("-f", "--force", action="store_true",
                         default=False, help=_("Deep scan mode"))

        self.parser.add_option_group(group)
    
    def run(self):
        self.init(database=True, write=False)
        installed = self.installdb.list_installed()
        installed.sort()
        install_files = util.AdvancedList(7)
        fail_list = []

        for pkg in installed:
            pkgname = pkg
            files = self.installdb.get_files(pkg)
            for f in files.list:
                #sys.stderr.write("\x1b[K"+_("Checking: {}").format(f.path)+"\r")
                if install_files.exists(f.path):
                    fail_list.append(f.path)
                    ctx.ui.warning(_("Found integration issue {}").format(f.path))
                else:
                    install_files.add(f.path)
            ctx.ui.info(_("[{}/{}] {} => ({} / {}) files counted.").format(installed.index(pkg)+1,len(installed),pkgname,len(files.list), install_files.length()))
            ctx.ui.verbose("Key length: {} / Ratio: {} \n".format(len(install_files.keys()),install_files.length()/len(install_files.keys())))
        ctx.ui.warning(_("List of integration issues:"))
        fail_list.sort()
        for path in fail_list:
            ctx.ui.warning("  /{}".format(path))

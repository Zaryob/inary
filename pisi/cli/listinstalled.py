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

import pisi.cli.command as command
import pisi.context as ctx
import pisi.api
import pisi.db

class ListInstalled(command.Command):
    """Print the list of all installed packages

Usage: list-installed
"""

    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListInstalled, self).__init__(args)
        self.installdb = pisi.db.installdb.InstallDB()
        self.componentdb = pisi.db.componentdb.ComponentDB()

    name = ("list-installed", "li")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("list-installed options"))

        group.add_option("-l", "--long", action="store_true",
                               default=False, help=_("Show in long format"))
        group.add_option("-c", "--component", action="store",
                               default=None, help=_("List installed packages under given component"))
        group.add_option("-i", "--install-info", action="store_true",
                               default=False, help=_("Show detailed install info"))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database = True, write = False)
        installed = self.installdb.list_installed()

        component = ctx.get_option('component')
        if component:
            #FIXME: pisi api is insufficient to do this
            from sets import Set as set
            component_pkgs = self.componentdb.get_union_packages(component, walk=True)
            installed = list(set(installed) & set(component_pkgs))

        installed.sort()
        if self.options.install_info:
            ctx.ui.info(_('Package Name     |St|   Version|  Rel.| Build|  Distro|             Date'))
            print         '========================================================================'
        for pkg in installed:
            package = self.installdb.get_package(pkg)
            inst_info = self.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(unicode(package))
                ctx.ui.info(unicode(inst_info))
            elif self.options.install_info:
                ctx.ui.info('%-15s  |%s' % (package.name, inst_info.one_liner()))
            else:
                ctx.ui.info('%15s - %s' % (package.name, unicode(package.summary)))

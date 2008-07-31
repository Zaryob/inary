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
import pisi.util as util
import pisi.api
import pisi.db

class ListAvailable(command.Command):
    """List available packages in the repositories

Usage: list-available [ <repo1> <repo2> ... repon ]

Gives a brief list of PiSi packages published in the specified
repositories. If no repository is specified, we list packages in
all repositories.
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListAvailable, self).__init__(args)
        self.componentdb = pisi.db.componentdb.ComponentDB()
        self.packagedb = pisi.db.packagedb.PackageDB()

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
            for repo in pisi.api.list_repos():
                ctx.ui.info(_("Repository : %s\n") % repo)
                self.print_packages(repo)

    def print_packages(self, repo):

        component = ctx.get_option('component')
        if component:
            try:
                l = self.componentdb.get_packages(component, repo=repo, walk=True)
            except Exception, e:
                ctx.ui.info(_("Component %s not found in %s repository") % (component, repo))
                return
        else:
            l = pisi.api.list_available(repo)
        installed_list = pisi.api.list_installed()
        l.sort()
        for p in l:
            package = self.packagedb.get_package(p, repo)
            if self.options.long:
                ctx.ui.info(unicode(package))
            else:
                lenp = len(p)
                if p in installed_list:
                    if ctx.config.get_option('uninstalled'):
                        continue
                    p = util.colorize(p, 'green')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s ' % (p, unicode(package.summary)))

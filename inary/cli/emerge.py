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

import inary.db
import inary.cli.command as command
import inary.cli.build as build
import inary.context as ctx
import inary.operations.emerge as emerge


class Emerge(build.Build, metaclass=command.autocommand):
    __doc__ = _("""Build and install INARY source packages from repository

Usage: emerge <sourcename> ...

You should give the name of a source package to be
downloaded from a repository containing sources.

You can also give the name of a component.
""")

    def __init__(self, args):
        super(Emerge, self).__init__(args)
        self.scom = True

    name = ("emerge", "em")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("emerge options"))
        group.add_option("-c", "--component", action="store",
                         default=None, help=_("Emerge available packages under given component"))
        group.add_option("--ignore-file-conflicts", action="store_true",
                         default=False, help=_("Ignore file conflicts"))
        group.add_option("--ignore-package-conflicts", action="store_true",
                         default=False, help=_("Ignore package conflicts"))
        group.add_option("--ignore-scom", action="store_true",
                         default=False, help=_("Bypass scom configuration agent"))
        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True)

        component = ctx.get_option('component')
        if not self.args and not component:
            self.help()
            return

        if component:
            componentdb = inary.db.componentdb.ComponentDB()
            sources = componentdb.get_union_sources(component, walk=True)
        else:
            sources = self.args

        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: {}').format(ctx.config.options.output_dir))
        else:
            ctx.ui.info(_('Outputting binary packages in the package cache.'))
            ctx.config.options.output_dir = ctx.config.cached_packages_dir()

        emerge.emerge(sources)

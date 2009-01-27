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
import pisi.cli.build as build
import pisi.context as ctx
import pisi.api

class Emerge(build.Build):
    __doc__ = _("""Build and install PiSi source packages from repository

Usage: emerge <sourcename> ...

You should give the name of a source package to be
downloaded from a repository containing sources.

You can also give the name of a component.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Emerge, self).__init__(args)
        self.comar = True

    name = ("emerge", "em")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("emerge options"))
        super(Emerge, self).add_options(group)
        group.add_option("-c", "--component", action="store",
                               default=None, help=_("Emerge available packages under given component"))
        group.add_option("--ignore-file-conflicts", action="store_true",
                     default=False, help=_("Ignore file conflicts"))
        group.add_option("--ignore-package-conflicts", action="store_true",
                     default=False, help=_("Ignore package conflicts"))
        group.add_option("--ignore-comar", action="store_true",
                               default=False, help=_("Bypass comar configuration agent"))
        self.parser.add_option_group(group)

    def run(self):
        self.init(database = True)

        component = ctx.get_option('component')
        if not self.args and not component:
            self.help()
            return

        if component:
            componentdb = pisi.db.componentdb.ComponentDB()
            sources = componentdb.get_union_sources(component, walk=True)
        else:
            sources = self.args

        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: %s') % ctx.config.options.output_dir)
        else:
            ctx.ui.info(_('Outputting binary packages in the package cache.'))
            ctx.config.options.output_dir = ctx.config.cached_packages_dir()

        pisi.api.emerge(sources)


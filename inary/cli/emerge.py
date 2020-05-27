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

import inary.sysconf as sysconf
import inary.context as ctx
import inary.cli.build as build
import inary.cli.command as command
import inary.db
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Emerge(build.Build, metaclass=command.autocommand):
    __doc__ = _("""Build and install INARY source packages from repository

Usage: emerge <sourcename> ...

You should give the name of a source package to be
downloaded from a repository containing sources.

You can also give the name of a component.
""")

    def __init__(self, args):
        super(Emerge, self).__init__(args)

    name = ("emerge", "em")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("emerge options"))
        group.add_option("-c", "--component", action="store",
                         default=None, help=_("Emerge available packages under given component"))
        group.add_option("--ignore-file-conflicts", action="store_true",
                         default=False, help=_("Ignore file conflicts."))
        group.add_option("--ignore-package-conflicts", action="store_true",
                         default=False, help=_("Ignore package conflicts."))
        group.add_option("--ignore-sysconf", action="store_true",
                         default=False, help=_("Skip sysconf operations after installation."))
        group.add_option("--force-sysconf", action="store_true",
                         default=False, help=_("Force sysconf operations after installation. Applies all sysconf operations"))

        self.parser.add_option_group(group)

    def run(self):
        from inary.operations import emerge
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
            ctx.ui.info(
                _('Output directory: {}').format(
                    ctx.config.options.output_dir))
        else:
            ctx.ui.info(_('Outputting binary packages in the package cache.'))
            ctx.config.options.output_dir = ctx.config.cached_packages_dir()

        emerge.emerge(sources)

        if not self.options.ignore_sysconf:
            sysconf.proceed(self.options.force_sysconf)

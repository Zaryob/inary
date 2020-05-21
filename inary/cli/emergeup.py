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
import inary.db
import inary.context as ctx
import inary.cli.build as build
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class EmergeUp(build.Build, metaclass=command.autocommand):
    __doc__ = _("""Build and upgrade INARY source packages from repository

Usage: emergeup ...

You should give the name of a source package to be
downloaded from a repository containing sources.

You can also give the name of a component.
""")

    def __init__(self, args):
        super(EmergeUp, self).__init__(args)

    name = ("emergeup", "emup")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("emergeup options"))
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
        from inary.operations import repository, emerge
        self.init(database=True)

        source = inary.db.sourcedb.SourceDB()

        imdb = inary.db.installdb.InstallDB()

        installed_emerge_packages = imdb.list_installed_with_build_host(
            "localhost")

        emerge_up_list = []

        for package in installed_emerge_packages:
            if source.has_spec(package):
                spec = source.get_spec(package)
                if spec.getSourceRelease() > imdb.get_version(package)[1]:
                    emerge_up_list.append(package)

        if ctx.get_option('output_dir'):
            ctx.ui.info(
                _('Output directory: {}').format(
                    ctx.config.options.output_dir))
        else:
            ctx.ui.info(_('Outputting binary packages in the package cache.'))
            ctx.config.options.output_dir = ctx.config.cached_packages_dir()

        repos = inary.db.repodb.RepoDB().list_repos(only_active=True)
        repository.update_repos(repos, ctx.get_option('force'))

        emerge.emerge(emerge_up_list)

        if not self.options.ignore_sysconf:
            sysconf.proceed(self.options.force_sysconf)

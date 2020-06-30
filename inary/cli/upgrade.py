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

import inary.util as util
import inary.sysconf as sysconf
import inary.db
import inary.context as ctx
import inary.cli.command as command
import gettext
import optparse

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Upgrade(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Upgrade INARY packages

Usage: Upgrade [<package1> <package2> ... <packagen>]

<packagei>: package name

Upgrades the entire system if no package names are given

You may use only package names to specify packages because
the package upgrade operation is defined only with respect
to repositories. If you have specified a package name, it
should exist in the package repositories. If you just want to
reinstall a package from a INARY file, use the install command.

You can also specify components instead of package names, which will be
expanded to package names.
""")

    def __init__(self, args):
        super(Upgrade, self).__init__(args)

    name = ("upgrade", "up")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("upgrade options"))

        super(Upgrade, self).options(group)
        group.add_option("--security-only", action="store_true",
                         default=False, help=_("Security related package upgrades only."))
        group.add_option("-b", "--bypass-update-repo", action="store_true",
                         default=False, help=_("Do not update repositories."))
        group.add_option("--ignore-file-conflicts", action="store_true",
                         default=False, help=_("Ignore file conflicts."))
        group.add_option("--ignore-package-conflicts", action="store_true",
                         default=False, help=_("Ignore package conflicts."))
        group.add_option("--ignore-sysconf", action="store_true",
                         default=False, help=_("Skip sysconf operations after installation."))
        group.add_option("--force-sysconf", action="store_true",
                         default=False, help=_("Force sysconf operations after installation. Applies all sysconf operations"))
        group.add_option("--preserve-permanent", action="store_true",
                         default=False,
                         help=_("Preserves permanent tagged files on upgrade action "
                                "like some important libc modules. This is used to be "
                                "sure about stability of system packages. This helps "
                                "you preserve your own source compiled applications "
                                "like pip modules, gem installations etc."))
        group.add_option("-c", "--component", action="append",
                         default=None, help=_("Upgrade component's and recursive components' packages."))
        group.add_option("-r", "--repository", action="store",
                         type="string", default=None, help=_('Name of the to be upgraded packages\' repository.'))
        group.add_option("-f", "--fetch-only", action="store_true",
                         default=False, help=_("Fetch upgrades but do not install."))
        group.add_option("-x", "--exclude", action="append",
                         default=None,
                         help=_("When upgrading system, ignore packages and components whose basenames match pattern."))
        group.add_option("--exclude-from", action="store",
                         default=None,
                         help=_("When upgrading system, ignore packages "
                                "and components whose basenames match "
                                "any pattern contained in file."))
        group.add_option("-s", "--compare-sha1sum", action="store_true",
                         default=False, help=_("Compare sha1sum repo and installed packages."))

        self.parser.add_option_group(group)

    def run(self):
        from inary.operations import repository, upgrade, helper
        if self.options.fetch_only:
            self.init(database=True, write=False)
        else:
            self.init()

        if not ctx.get_option('bypass_update_repo'):
            ctx.ui.info(_('Updating repositories.'), color='green')
            repos = inary.db.repodb.RepoDB().list_repos(only_active=True)
            repository.update_repos(repos)
        else:
            ctx.ui.info(_('Will not update repositories.'))

        reposit = ctx.get_option('repository')
        components = ctx.get_option('component')
        packages = []
        if components:
            componentdb = inary.db.componentdb.ComponentDB()
            for name in components:
                if componentdb.has_component(name):
                    if repository:
                        packages.extend(
                            componentdb.get_packages(
                                name, walk=True, repo=reposit))
                    else:
                        packages.extend(
                            componentdb.get_union_packages(
                                name, walk=True))
        packages.extend(self.args)

        upgrade.upgrade(packages, reposit)

        try:
            config_changes, opt = helper.check_config_changes(
                [util.parse_package_name_legacy(i.split("/")[-1])[0] for i in packages])
            if config_changes:
                if ctx.ui.confirm(
                        _("[!] Some config files have been changed. Would you like to see and apply them?")):
                    helper.show_changed_configs(config_changes, opt)
        except ValueError:
            pass

        if not self.options.ignore_sysconf:
            sysconf.proceed(self.options.force_sysconf)

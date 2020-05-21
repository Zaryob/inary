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
import inary.util as util
import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Install(command.PackageOp, metaclass=command.autocommand):
    __doc__ = _("""Install INARY packages

Usage: install <package1> <package2> ... <packagen>

You may use filenames, URI's or package names for packages. If you have
specified a package name, it should exist in a specified repository.

You can also specify components instead of package names, which will be
expanded to package names.
""")

    def __init__(self, args):
        super(Install, self).__init__(args)
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = "install", "it"

    def options(self):
        group = optparse.OptionGroup(self.parser, _("install options"))

        super(Install, self).options(group)

        group.add_option("--reinstall", action="store_true",
                         default=False, help=_("Reinstall already installed packages."))
        group.add_option("--ignore-check", action="store_true",
                         default=False, help=_("Skip distribution release and architecture check."))
        group.add_option("--ignore-configure", action="store_true",
                         default=False, help=_("Skip configure and mark configure pending."))
        group.add_option("--ignore-file-conflicts", action="store_true",
                         default=False, help=_("Ignore file conflicts."))
        group.add_option("--ignore-package-conflicts", action="store_true",
                         default=False, help=_("Ignore package conflicts."))
        group.add_option("--ignore-sysconf", action="store_true",
                         default=False, help=_("Skip sysconf operations after installation."))
        group.add_option("--force-sysconf", action="store_true",
                         default=False, help=_("Force sysconf operations after installation. Applies all sysconf operations"))
        group.add_option("-c", "--component", action="append",
                         default=None, help=_("Install component's and recursive components' packages."))
        group.add_option("-r", "--repository", action="store",
                         type="string", default=None, help=_('Name of the component\'s repository.'))
        group.add_option("-f", "--fetch-only", action="store_true",
                         default=False, help=_("Fetch upgrades but do not install."))
        group.add_option("-x", "--exclude", action="append",
                         default=None, help=_(
                             "When installing packages, ignore packages and components whose basenames match pattern."))
        group.add_option("--exclude-from", action="store",
                         default=None,
                         help=_("When installing packages, ignore packages "
                                "and components whose basenames match "
                                "any pattern contained in file."))
        group.add_option("-s", "--store-lib-info", action="store_true",
                         default=False,
                         help=_("Store previous libraries info when package is updating to newer version."))
        self.parser.add_option_group(group)

    def run(self):
        from inary.operations import install, helper
        if self.options.fetch_only:
            self.init(database=True, write=False)
        else:
            self.init()

        components = ctx.get_option('component')
        if not components and not self.args:
            self.help()
            return

        packages = []
        if components:
            for name in components:
                if self.componentdb.has_component(name):
                    repository = ctx.get_option('repository')
                    if repository:
                        packages.extend(
                            self.componentdb.get_packages(
                                name, walk=True, repo=repository))
                    else:
                        packages.extend(
                            self.componentdb.get_union_packages(
                                name, walk=True))
                else:
                    ctx.ui.info(
                        _('There is no component named  as \"{}\"').format(name))

        packages.extend(self.args)

        if ctx.get_option('exclude_from'):
            packages = inary.blacklist.exclude_from(
                packages, ctx.get_option('exclude_from'))

        if ctx.get_option('exclude'):
            packages = inary.blacklist.exclude(
                packages, ctx.get_option('exclude'))

        reinstall = bool(packages) and packages[0].endswith(
            ctx.const.package_suffix)
        install.install(packages, ctx.get_option('reinstall') or reinstall)

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

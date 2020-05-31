# -*- coding:utf-8 -*-
#
# Copyright (C) 2019 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General General Public License for more details.
#
# Please read the COPYING file.
#

# Standart Python Modules
import optparse

# Inary Modules
import inary.db
import inary.context as ctx
import inary.cli.command as command

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ConfigManager(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Inary Config file manager.""")

    def __init__(self, args):
        super(ConfigManager, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()

    name = "config-manager", "cm"

    def options(self):
        group = optparse.OptionGroup(self.parser, _("config-manager options"))

        group.add_option("--purge", action="store_true",
                         default=False, help=_("Rewrite all config files with new ones without keeping old config files."))
        group.add_option("--soft-keep", action="store_true",
                         default=False, help=_("Rewrite all config files with new ones, keeping old config files."))
        self.parser.add_option_group(group)

    def run(self):
        from inary.operations import helper
        self.init(database=True, write=True)

        config_changes = helper.check_config_changes(
            order=self.installdb.list_installed())

        if config_changes:
            if ctx.get_option('purge'):
                for package in config_changes:
                    if config_changes[package]:
                        for file in config_changes[package]:
                            helper.apply_changed_config(file, keep=False)
                return

            if ctx.get_option('soft-keep'):
                for package in config_changes:
                    if config_changes[package]:
                        for file in config_changes[package]:
                            helper.apply_changed_config(file, keep=True)
                return

            if ctx.ui.confirm(
                    _("[!] Some config files have been changed. Would you like to see and apply them?")):
                helper.show_changed_configs(config_changes)

        else:
            ctx.ui.info(_("There isn't any new config :)"), color='green')

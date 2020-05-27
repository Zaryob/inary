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

import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


usage = _("""Creates delta packages

Usages: delta oldpackage1 oldpackage2 ...  newpackage
        delta -t newpackage oldpackage1 oldpackage2 ...

Delta command finds the changed files between the given
packages by comparing the sha1sum of files and creates
a delta package with the changed files.
""")


class Delta(command.Command, metaclass=command.autocommand):
    __doc__ = usage

    def __init__(self, args):
        super(Delta, self).__init__(args)

    name = ("delta", "dt")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("delta options"))

        group.add_option("-t", "--newest-package",
                         action="store",
                         default=None,
                         help=_("Use arg as the new package and treat "
                                "other arguments as old packages."))

        group.add_option("-O", "--output-dir",
                         action="store",
                         default=None,
                         help=_("Output directory for produced packages."))

        group.add_option("-F", "--package-format",
                         action="store",
                         help=_("Create the binary package using the given "
                                "format. Use '-F help' to see a list of "
                                "supported formats."))
        self.parser.add_option_group(group)

    def run(self):
        import inary.operations
        self.init(database=False, write=False)

        if self.options.package_format == "help":
            ctx.ui.info(_("Supported package formats:"))
            for format in inary.package.Package.formats:
                if format == inary.package.Package.default_format:
                    ctx.ui.info(_("  {} (default)").format(format))
                else:
                    ctx.ui.info("  {}".format(format))
            return

        new_package = ctx.get_option("newest_package")
        if new_package:
            old_packages = self.args
        else:
            if len(self.args) < 2:
                self.help()
                return

            new_package = self.args[-1]
            old_packages = self.args[:-1]

        if not ctx.get_option('output_dir'):
            ctx.config.options.output_dir = '.'

        from inary.operations.delta import create_delta_packages
        create_delta_packages(old_packages, new_package)

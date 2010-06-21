# -*- coding:utf-8 -*-
#
# Copyright (C) 2005-2010, TUBITAK/UEKAE
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

import pisi
import pisi.cli.command as command
import pisi.context as ctx


usage = _("""Creates delta PiSi packages

Usage: delta oldpackage newpackage

Delta command finds the changed files between the given
packages by comparing the sha1sum of the files and creates
a delta pisi package with the changed files between two
releases.
""")


class Delta(command.Command):

    __doc__ = usage
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Delta, self).__init__(args)

    name = ("delta", "dt")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("delta options"))
        self.add_options(group)
        self.parser.add_option_group(group)

    def add_options(self, group):
        group.add_option("-O", "--output-dir",
                         action="store",
                         default=None,
                         help=_("Output directory for produced packages"))

        group.add_option("-F", "--package-format",
                         action="store",
                         help=_("Create the binary package using the given "
                                "format. Use '-F help' to see a list of "
                                "supported formats."))

    def run(self):
        from pisi.operations.delta import create_delta_package

        self.init(database=False, write=False)

        if self.options.package_format == "help":
            ctx.ui.info(_("Supported package formats:"))
            for format in pisi.package.Package.formats:
                if format == pisi.package.Package.default_format:
                    ctx.ui.info(_("  %s (default)") % format)
                else:
                    ctx.ui.info("  %s" % format)
            return

        if len(self.args) != 2:
            self.help()
            return

        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: %s')
                        % ctx.config.options.output_dir)
        else:
            ctx.ui.info(_('Outputting packages in the working directory.'))
            ctx.config.options.output_dir = '.'

        oldpackage = self.args[0]
        newpackage = self.args[1]

        create_delta_package(oldpackage, newpackage)

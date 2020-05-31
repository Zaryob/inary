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

# Standart Python Modules
import optparse

# Inary Modules
import inary.context as ctx
import inary.cli.command as command

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


usage = _("""Build INARY packages

Usage: build [<pspec.xml> | <sourcename>] ...

You can give a URI of the pspec.xml file. INARY will
fetch all necessary files and build the package for you.

Alternatively, you can give the name of a source package
to be downloaded from a repository containing sources.
""")


class Build(command.Command, metaclass=command.autocommand):
    __doc__ = usage

    def __init__(self, args):
        super(Build, self).__init__(args)

    name = ("build", "bi")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("build options"))

        group.add_option("-q", "--quiet",
                         action="store_true",
                         default=False,
                         help=_("Run inary build operation without printing "
                                "extra debug information."))

        group.add_option("--ignore-dependency",
                         action="store_true",
                         default=False,
                         help=_("Do not take dependency information into "
                                "account."))

        group.add_option("-O", "--output-dir",
                         action="store",
                         default=None,
                         help=_("Output directory for produced packages."))

        group.add_option("--ignore-verify",
                         action="store_true",
                         default=False,
                         help=_("Bypass sha1sum verify step of source archive."))

        group.add_option("--ignore-action-errors",
                         action="store_true", default=False,
                         help=_("Bypass errors from ActionsAPI."))

        group.add_option("--ignore-safety",
                         action="store_true",
                         default=False,
                         help=_("Bypass safety switch."))

        group.add_option("--ignore-check",
                         action="store_true",
                         default=False,
                         help=_("Bypass testing step."))

        group.add_option("--create-static",
                         action="store_true",
                         default=False,
                         help=_("Create a static package with ar files."))

        group.add_option("-F", "--package-format",
                         action="store",
                         help=_("Create the binary package using the given "
                                "format. Use '-F help' to see a list of "
                                "supported formats."))

        group.add_option("--use-quilt",
                         action="store_true",
                         default=False,
                         help=_("Use quilt patch management system "
                                "instead of GNU patch."))

        self.parser.add_option_group(group)
        group = optparse.OptionGroup(self.parser, _("build steps"))

        group.add_option("--fetch",
                         dest="until",
                         action="store_const",
                         const="fetch",
                         help=_("Break build after fetching the source "
                                "archive."))

        group.add_option("--unpack",
                         dest="until",
                         action="store_const",
                         const="unpack",
                         help=_("Break build after unpacking the source "
                                "archive, checking sha1sum and applying "
                                "patches."))

        group.add_option("--setup",
                         dest="until",
                         action="store_const",
                         const="setup",
                         help=_("Break build after running configure step."))

        group.add_option("--build",
                         dest="until",
                         action="store_const",
                         const="build",
                         help=_("Break build after running compile step."))

        group.add_option("--check",
                         dest="until",
                         action="store_const",
                         const="check",
                         help=_("Break build after running check step."))

        group.add_option("--install",
                         dest="until",
                         action="store_const",
                         const="install",
                         help=_("Break build after running install step."))

        group.add_option("--package",
                         dest="until",
                         action="store_const",
                         const="package",
                         help=_("Create INARY package."))

        self.parser.add_option_group(group)

    def run(self):
        import inary.operations

        if not self.options.quiet:
            self.options.debug = True

        if self.options.package_format == "help":
            ctx.ui.info(_("Supported package formats:"))
            for format in inary.package.Package.formats:
                if format == inary.package.Package.default_format:
                    ctx.ui.info(_("  {} (default)").format(format))
                else:
                    ctx.ui.info("  {}".format(format))
            return

        self.init(False, False)

        if not ctx.get_option('output_dir'):
            ctx.config.options.output_dir = '.'

        for x in self.args or ["pspec.xml"]:
            if ctx.get_option('until'):
                inary.operations.build.build_until(x, ctx.get_option('until'))
            else:
                inary.operations.build.build(x)

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

import pisi.api
import pisi.cli.command as command
import pisi.context as ctx

class Build(command.Command):
    """Build PiSi packages

Usage: build [<pspec.xml> | <sourcename>] ...

You can give a URI of the pspec.xml file. PiSi will
fetch all necessary files and build the package for you.

Alternatively, you can give the name of a source package
to be downloaded from a repository containing sources.
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Build, self).__init__(args)
        self.comar = True

    name = ("build", "bi")

    package_formats = ('1.0', '1.1')

    def options(self):

        self.add_steps_options()
        group = optparse.OptionGroup(self.parser, _("build options"))
        self.add_options(group)
        self.parser.add_option_group(group)

    def add_options(self, group):
        group.add_option("--ignore-build-no", action="store_true",
                               default=False,
                               help=_("Do not take build no into account."))
        group.add_option("--ignore-dependency", action="store_true",
                               default=False,
                               help=_("Do not take dependency information into account"))
        group.add_option("-O", "--output-dir", action="store", default=None,
                               help=_("Output directory for produced packages"))
        group.add_option("--ignore-action-errors",
                               action="store_true", default=False,
                               help=_("Bypass errors from ActionsAPI"))
        group.add_option("--ignore-safety", action="store_true",
                     default=False, help=_("Bypass safety switch"))
        group.add_option("--ignore-check", action="store_true",
                     default=False, help=_("Bypass testing step"))
        group.add_option("--create-static", action="store_true",
                               default=False, help=_("Create a static package with ar files"))
        group.add_option("--no-install", action="store_true",
                               default=False, help=_("Do not install build dependencies, fail if a build dependency is present"))
        group.add_option("-F", "--package-format", action="store", default='1.1',
                               help=_("PiSi binary package formats: '1.0', '1.1' (default)"))
        group.add_option("--use-quilt", action="store_true", default=False,
                               help=_("Use quilt patch management system instead of GNU patch"))
        group.add_option("--ignore-sandbox", action="store_true", default=False,
                               help=_("Do not constrain build process inside the build folder"))

    def add_steps_options(self):
        group = optparse.OptionGroup(self.parser, _("build steps"))
        group.add_option("--fetch", dest="until", action="store_const",
                         const="fetch", help=_("Break build after fetching the source archive"))
        group.add_option("--unpack", dest="until", action="store_const",
                         const="unpack", help=_("Break build after unpacking the source archive, checking sha1sum and applying patches"))
        group.add_option("--setup", dest="until", action="store_const",
                         const="setup", help=_("Break build after running configure step"))
        group.add_option("--build", dest="until", action="store_const",
                         const="build", help=_("Break build after running compile step"))
        group.add_option("--check", dest="until", action="store_const",
                         const="check", help=_("Break build after running check step"))
        group.add_option("--install", dest="until", action="store_const",
                         const="install", help=_("Break build after running install step"))
        group.add_option("--package", dest="until", action="store_const",
                         const="package", help=_("create PiSi package"))
        self.parser.add_option_group(group)

    def run(self):
        if not self.args:
            self.help()
            return

        if self.options.no_install:
            self.init(database=True, write=False)
        else:
            self.init()

        if ctx.get_option('package_format') not in Build.package_formats:
            raise Error(_('package_format must be one of %s ') % pisi.util.strlist(Build.package_formats))

        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: %s') % ctx.config.options.output_dir)
        else:
            ctx.ui.info(_('Outputting packages in the working directory.'))
            ctx.config.options.output_dir = '.'

        for x in self.args:
            if ctx.get_option('until'):
                pisi.api.build_until(x, ctx.get_option('until'))
            else:
                pisi.api.build(x)

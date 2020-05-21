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

import inary.operations.info as info_operation
import inary.db
import inary.util as util
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Info(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Display package information

Usage: info <package1> <package2> ... <packagen>

<packagei> is either a package name or a .inary file,
""")

    def __init__(self, args):
        super(Info, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()
        self.componentdb = inary.db.componentdb.ComponentDB()
        self.packagedb = inary.db.packagedb.PackageDB()
        self.sourcedb = inary.db.sourcedb.SourceDB()

    name = ("info", None)

    def options(self):

        group = optparse.OptionGroup(self.parser, _("info options"))

        group.add_option("-f", "--files", action="store_true",
                         default=False,
                         help=_("Show a list of package files."))
        group.add_option("-c", "--component", action="append",
                         default=None, help=_("Info about the given component."))
        group.add_option("-F", "--files-path", action="store_true",
                         default=False,
                         help=_("Show only paths."))
        group.add_option("-s", "--short", action="store_true",
                         default=False, help=_("Do not show details."))
        group.add_option("--xml", action="store_true",
                         default=False, help=_("Output in xml format."))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database=True, write=False)

        components = ctx.get_option('component')
        if not components and not self.args:
            self.help()
            return

        index = inary.data.index.Index()
        index.distribution = None

        # info of components
        if components:
            for name in components:
                if self.componentdb.has_component(name):
                    component = self.componentdb.get_union_component(name)
                    if self.options.xml:
                        index.add_component(component)
                    else:
                        if not self.options.short:
                            ctx.ui.info(str(component))
                        else:
                            ctx.ui.info(
                                "{0.name} - {0.summary}".format(component))

        # info of packages
        for arg in self.args:
            if self.options.xml:
                index.packages.append(info_operation.info(arg)[0].package)
            else:
                self.info_package(arg)

        if self.options.xml:
            import sys
            errs = []
            index.newDocument()
            index.encode(index.rootNode(), errs)
            index.writexmlfile(sys.stdout)
            sys.stdout.write('\n')

    def info_package(self, arg):

        if arg.endswith(ctx.const.package_suffix):
            self.inaryfile_info(arg)
            return

        self.installdb_info(arg)
        self.packagedb_info(arg)
        self.sourcedb_info(arg)

    def print_files(self, files):
        files.list.sort(key=lambda x: x.path)
        for fileinfo in files.list:
            if self.options.files:
                print(fileinfo)
            else:
                print("/" + fileinfo.path)

    @staticmethod
    def print_metadata(metadata, packagedb=None):
        if ctx.get_option('short'):
            pkg = metadata.package
            ctx.ui.formatted_output(" - ".join((pkg.name, str(pkg.summary))))
        else:
            ctx.ui.formatted_output(str(metadata.package))
            if packagedb:
                revdeps = [
                    name for name,
                    dep in packagedb.get_rev_deps(
                        metadata.package.name)]
                ctx.ui.formatted_output(
                    " ".join(
                        (_("Reverse Dependencies:"), util.strlist(revdeps))))
                print()

    @staticmethod
    def print_specdata(spec, sourcedb=None):
        src = spec.source
        if ctx.get_option('short'):
            ctx.ui.formatted_output(" - ".join((src.name, str(src.summary))))
        else:
            ctx.ui.formatted_output(str(spec))
            if sourcedb:
                revdeps = [
                    name for name,
                    dep in sourcedb.get_rev_deps(
                        spec.source.name)]
                print(_('Reverse Build Dependencies:'), util.strlist(revdeps))
                print()

    def inaryfile_info(self, package):
        metadata, files = info_operation.info_file(package)
        ctx.ui.formatted_output(_("Package file: \"{}\"").format(package))

        self.print_metadata(metadata)
        if self.options.files or self.options.files_path:
            self.print_files(files)

    def installdb_info(self, package):
        if self.installdb.has_package(package):
            metadata, files, repo = info_operation.info_name(package, True)

            if self.options.files or self.options.files_path:
                self.print_files(files)
                return

            if self.options.short:
                ctx.ui.formatted_output(_("[inst] "), noln=True, column=" ")
            else:
                ctx.ui.info(_('Installed package:'))

            self.print_metadata(metadata, self.installdb)
        else:
            ctx.ui.info(_("\"{}\" package is not installed.").format(package))

    def packagedb_info(self, package):
        if self.packagedb.has_package(package):
            metadata, files, repo = info_operation.info_name(package, False)
            if self.options.short:
                ctx.ui.formatted_output(_("[binary] "), noln=True, column=" ")
            else:
                ctx.ui.info(
                    _('Package found in \"{}\" repository:').format(repo))
            self.print_metadata(metadata, self.packagedb)
        else:
            ctx.ui.info(
                _("\"{}\" package is not found in binary repositories.").format(package))

    def sourcedb_info(self, package):
        if self.sourcedb.has_spec(package):
            repo = self.sourcedb.which_repo(package)
            spec = self.sourcedb.get_spec(package)
            if self.options.short:
                ctx.ui.formatted_output(_("[source] "), noln=True, column=" ")
            else:
                ctx.ui.info(
                    _('Package found in \"{}\" repository:').format(repo))
            self.print_specdata(spec, self.sourcedb)
        else:
            ctx.ui.info(
                _("\"{}\" package is not found in source repositories.").format(package))

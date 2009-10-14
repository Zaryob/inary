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
import re

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.cli.command as command
import pisi.context as ctx
import pisi.db

class Search(command.Command):
    __doc__ = _("""Search packages

Usage: search <term1> <term2> ... <termn>

Finds a package containing specified search terms
in summary, description, and package name fields.
Default search is done in package database. Use
options to search in install database or source
database.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Search, self).__init__(args)

    name = ("search", "sr")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("search options"))
        group.add_option("-l", "--language", action="store",
                               type="string", default=None, help=_('Summary and description language'))
        group.add_option("-r", "--repository", action="store",
                               type="string", default=None, help=_('Name of the source or package repository'))
        group.add_option("-i", "--installdb", action="store_true",
                               default=False, help=_("Search in installdb"))
        group.add_option("-s", "--sourcedb", action="store_true",
                               default=False, help=_("Search in sourcedb"))
        group.add_option("--name", action="store_true",
                               default=False, help=_('Search in the package name'))
        group.add_option("--summary", action="store_true",
                               default=False, help=_('Search in the package summary'))
        group.add_option("--description", action="store_true",
                               default=False, help=_('Search in the package description'))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database = True, write = False)

        if not self.args:
            self.help()
            return

        replace = re.compile("(%s)" % "|".join(self.args), re.I)
        lang = ctx.get_option('language')
        repo = ctx.get_option('repository')
        name = ctx.get_option('name')
        summary = ctx.get_option('summary')
        desc = ctx.get_option('description')
        fields = None
        if name or summary or desc:
            fields = {'name': name, 'summary': summary, 'desc': desc}

        if ctx.get_option('installdb'):
            db = pisi.db.installdb.InstallDB()
            pkgs = db.search_package(self.args, lang, fields)
            get_info = db.get_package
            get_name_sum = lambda pkg:(pkg.name, pkg.summary)
        elif ctx.get_option('sourcedb'):
            db = pisi.db.sourcedb.SourceDB()
            pkgs = db.search_spec(self.args, lang, repo, fields)
            get_info = db.get_spec
            get_name_sum = lambda pkg:(pkg.source.name, pkg.source.summary)
        else:
            db = pisi.db.packagedb.PackageDB()
            pkgs = db.search_package(self.args, lang, repo, fields)
            get_info = db.get_package
            get_name_sum = lambda pkg:(pkg.name, pkg.summary)

        for pkg in pkgs:
            pkg_info = get_info(pkg)
            name, summary = get_name_sum(pkg_info)
            name = replace.sub(pisi.util.colorize(r"\1", "brightred"), name)
            if lang and summary.has_key(lang):
                summary = replace.sub(pisi.util.colorize(r"\1", "brightred"), str(summary[lang]))
            else:
                summary = replace.sub(pisi.util.colorize(r"\1", "brightred"), str(summary))

            print "%s - %s" % (name, summary)

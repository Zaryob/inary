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

import pisi.cli.command as command
import pisi.context as ctx


usage = _("""Index PiSi files in a given directory

Usage: index <directory> ...

This command searches for all PiSi files in a directory, collects PiSi
tags from them and accumulates the information in an output XML file,
named by default 'pisi-index.xml'. In particular, it indexes both
source and binary packages.

If you give multiple directories, the command still works, but puts
everything in a single index file.
""")


class Index(command.Command):

    __doc__ = usage
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Index, self).__init__(args)

    name = ("index", "ix")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("index options"))

        group.add_option("-a", "--absolute-urls",
                         action="store_true",
                         default=False,
                         help=_("Store absolute links for indexed files."))

        group.add_option("-o", "--output",
                         action="store",
                         default='pisi-index.xml',
                         help=_("Index output file"))

        group.add_option("--compression-types",
                         action="store",
                         default="xz",
                         help=_("Comma-separated compression types "
                                "for index file"))

        group.add_option("--skip-sources",
                         action="store_true",
                         default=False,
                         help=_("Do not index PiSi spec files."))

        group.add_option("--skip-signing",
                         action="store_true",
                         default=False,
                         help=_("Do not sign index."))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)

        from pisi.api import index
        from pisi.file import File

        ctypes = {"bz2": File.COMPRESSION_TYPE_BZ2,
                  "xz": File.COMPRESSION_TYPE_XZ}
        compression = 0
        for type_str in ctx.get_option("compression_types").split(","):
            compression |= ctypes.get(type_str, 0)

        index(self.args or ["."], ctx.get_option('output'),
              skip_sources=ctx.get_option('skip_sources'),
              skip_signing=ctx.get_option('skip_signing'),
              compression=compression)

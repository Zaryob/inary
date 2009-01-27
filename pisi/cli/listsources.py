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

import pisi.cli.command as command
import pisi.context as ctx
import pisi.db

class ListSources(command.Command):
    __doc__ = _("""List available sources

Usage: list-sources

Gives a brief list of sources published in the repositories.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListSources, self).__init__(args)
        self.sourcedb = pisi.db.sourcedb.SourceDB()

    name = ("list-sources", "ls")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("list-sources options"))
        group.add_option("-l", "--long", action="store_true",
                               default=False, help=_("Show in long format"))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database = True, write = False)

        l = self.sourcedb.list_sources()
        l.sort()
        for p in l:
            sf, repo = self.sourcedb.get_spec_repo(p)
            if self.options.long:
                ctx.ui.info('[Repository: ' + repo + ']')
                ctx.ui.info(unicode(sf.source))
            else:
                lenp = len(p)
                #if p in installed_list:
                #    p = util.colorize(p, 'cyan')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s' % (sf.source.name, unicode(sf.source.summary)))

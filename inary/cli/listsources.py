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

import inary.util as util
import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ListSources(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List available sources

Usage: list-sources

Gives a brief list of sources published in the repositories.
""")

    def __init__(self, args):
        super(ListSources, self).__init__(args)
        self.sourcedb = inary.db.sourcedb.SourceDB()

    name = ("list-sources", "ls")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("list-sources options"))
        group.add_option("-l", "--long", action="store_true",
                         default=False, help=_("Show in long format"))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database=True, write=False)

        l = self.sourcedb.list_sources()

        if l:
            maxlen = max([len(_p) for _p in l])

        installed_list = inary.db.sourcedb.SourceDB().list_sources()
        l.sort()

        for p in l:
            sf, repo = self.sourcedb.get_spec_repo(p)
            if self.options.long:
                ctx.ui.info(_('[Repository: ') + repo + ']')
                ctx.ui.info(str(sf.source))
            else:
                if p in installed_list:
                    sf.source.name = util.colorize(sf.source.name, 'cyan')
                sf.source.name += ' ' * max(0, maxlen - len(p))
                ctx.ui.info('{0} - {1}'.format(sf.source.name,
                                               str(sf.source.summary)))

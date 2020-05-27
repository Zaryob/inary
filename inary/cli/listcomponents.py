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

import inary.db
import inary.context as ctx
import inary.cli.command as command
import optparse

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ListComponents(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List available components

Usage: list-components

Gives a brief list of INARY components published in the
repositories.
""")

    def __init__(self, args):
        super(ListComponents, self).__init__(args)
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = ("list-components", "lc")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("list-components options"))
        group.add_option("-l", "--long", action="store_true",
                         default=False, help=_("Show in long format"))
        group.add_option("-r", "--repository", action="store",
                         type="string", default=None, help=_('Name of the source or package repository'))
        self.parser.add_option_group(group)

    def run(self):

        self.init(database=True, write=False)

        l = self.componentdb.list_components(ctx.get_option('repository'))
        if l:
            maxlen = max([len(_p) for _p in l])
        l.sort()
        for p in l:
            component = self.componentdb.get_component(p)
            if self.options.long:
                ctx.ui.info(str(component))
            else:
                component.name += ' ' * max(0, maxlen - len(p))
                ctx.ui.info('{0} - {1} '.format(component.name,
                                                str(component.summary)))

# -*- coding:utf-8 -*-
#
# Copyright (C) 2016  -  2017,  Suleyman POYRAZ (Zaryob)
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
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.db

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

        self.init(database = True, write = False)

        l = self.componentdb.list_components(ctx.get_option('repository'))
        l.sort()
        for p in l:
            component = self.componentdb.get_component(p)
            if self.options.long:
                ctx.ui.info(str(component))
            else:
                lenp = len(p)
                #if p in installed_list:
                #    p = util.colorize(p, 'cyan')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s ' % (component.name, str(component.summary)))

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

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.reactor as Reactor

class ListPending(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List pending packages

Lists packages waiting to be configured.
""")

    def __init__(self, args):
        super(ListPending, self).__init__(args)

    name = ("list-pending", "lp")

    def run(self):
        self.init(database = True, write = False)

        A = Reactor.list_pending()
        if len(A):
            for p in Reactor.generate_pending_order(A):
                sys.stdout.write(p)
        else:
            ctx.ui.info(_('There are no packages waiting to be configured'))
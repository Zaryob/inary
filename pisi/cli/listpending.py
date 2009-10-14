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

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.cli.command as command
import pisi.context as ctx
import pisi.api

class ListPending(command.Command):
    __doc__ = _("""List pending packages

Lists packages waiting to be configured.
""")
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(ListPending, self).__init__(args)

    name = ("list-pending", "lp")

    def run(self):
        self.init(database = True, write = False)

        A = pisi.api.list_pending()
        if len(A):
            for p in pisi.api.generate_pending_order(A):
                print p
        else:
            ctx.ui.info(_('There are no packages waiting to be configured'))

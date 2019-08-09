# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.data.pgraph
import inary.db


class ListPending(command.Command, metaclass=command.autocommand):
    __doc__ = _("""List pending packages

Lists packages waiting to be configured.
""")

    def __init__(self, args):
        super(ListPending, self).__init__(args)

    name = ("list-pending", "lp")

    def run(self):
        self.init(database=True, write=False)

        A = inary.db.installdb.InstallDB().list_pending()
        if len(A):
            ctx.ui.info(_('Listing pending orders:'), color='blue')
            for p in inary.data.pgraph.generate_pending_order(A):
                ctx.ui.info(p)
        else:
            ctx.ui.info(_('There are no packages waiting to be configured'))

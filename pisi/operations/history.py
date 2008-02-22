# -*- coding: utf-8 -*-
#
# Copyright (C) 2008, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import gettext
__trans = gettext.translation("pisi", fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.util
import pisi.db

def __listactions(actions):
    beinstalled = []
    beremoved = []

    for pkg in actions:
        action, version = actions[pkg]
        if action == "install":
            beinstalled.append("%s-%s" % (pkg, version))
        else:
            beremoved.append("%s" % pkg)

    return beinstalled, beremoved

def takeback(operation):

    historydb = pisi.db.historydb.HistoryDB()
    actions = {}

    for operation in historydb.get_till_operation(operation):
        if operation == "snapshot":
            pass

        for pkg in operation.packages:
            if pkg.operation in ["upgrade", "downgrade", "remove"]:
                actions[pkg.name] = ("install", pkg.before)
            if pkg.operation == "install":
                actions[pkg.name] = ("remove", None)

    beinstalled, beremoved = __listactions(actions)

    if beinstalled:
        ctx.ui.info(_("Following packages will be installed:\n") + pisi.util.strlist(beinstalled))

    if beremoved:
        ctx.ui.info(_("Following packages will be removed:\n") + pisi.util.strlist(beremoved))

    if (beremoved or beinstalled) and not ctx.ui.confirm(_('Do you want to continue?')):
        return

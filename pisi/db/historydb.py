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
#

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import piksemel

import pisi.db.lazydb as lazydb
import pisi.history

class HistoryDB(lazydb.LazyDB):

    def init(self):
        pass

    def __generate_history(self, doc):
        pass

    def create(self, operation):
        self.history = pisi.history.History()
        self.history.create(operation)

    def update(self, pkgBefore=None, pkgAfter=None, operation=None):
        self.history.add(pkgBefore, pkgAfter, operation)
        self.history.update()

# -*- coding: utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import inary.db.lazydb as lazydb

class TestDB(lazydb.LazyDB):

    def init(self):
        self.testfield = True

    def getTestField(self):
        return self.testfield

class LazyDBTestCase(unittest.TestCase):

    def testDatabaseMethodForcingInit(self):
        db = TestDB()
        assert db.getTestField()
        assert "testfield" in db.__dict__
        db._delete()

    def testDatabaseWithoutInit(self):
        db = TestDB()
        assert "testfield" not in db.__dict__
        db._delete()

    def testSingletonBehaviour(self):
        db = TestDB()
        db2 = TestDB()
        assert id(db) == id(db2)

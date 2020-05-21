# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
from . import testcase
import inary.db.lazydb as lazydb


class TestDB(lazydb.LazyDB):

    def init(self):
        self.testfield = True

    def getTestField(self):
        return self.testfield


class LazyDBTestCase(testcase.TestCase):

    def testDatabaseMethodForcingInit(self):
        db = TestDB()
        assert db.getTestField()
        assert "testfield" in db.__dict__
        db._delete()

    def testDatabaseWithoutInit(self):
        db = TestDB()
        assert not "testfield" in db.__dict__
        db._delete()

    def testSingletonBehaviour(self):
        db = TestDB()
        db2 = TestDB()
        assert id(db) == id(db2)

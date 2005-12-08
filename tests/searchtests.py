# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import os

import pisi.search
import pisi.lockeddbshelve

import testcase

class SearchTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database = False)
        pisi.lockeddbshelve.init_dbenv()

    def testSearch(self):
        doc1 = "A set object is an unordered collection of immutable values."
        doc2 = "Being an unordered collection, sets do not record element position or order of insertion."
        doc3 = "There are currently two builtin set types, set and frozenset"
        pisi.search.init(['test'], ['en'])
        pisi.search.add_doc('test', 'en', 1, doc1)
        pisi.search.add_doc('test', 'en', 2, doc2)
        pisi.search.add_doc('test', 'en', 3, doc3)
        q1 = pisi.search.query('test', 'en', ['set'])
        self.assertEqual(q1, set([1,3]))
        q2 = pisi.search.query('test', 'en', ['an', 'collection'])
        self.assertEqual(q2, set([1,2]))
        pisi.search.finalize()

suite = unittest.makeSuite(SearchTestCase)

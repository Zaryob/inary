# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# Please read the COPYING file.
#

import unittest
from . import testcase
import os
import inary.operations.search
import inary.db as db


class SearchTestCase(testcase.TestCase):
    def setUp(self):
        testcase.TestCase.setUp(self)

    def testSearch(self):
        doc1 = "A set object is an unordered collection of immutable values."
        doc2 = "Being an unordered collection, sets do not record element position or order of insertion."
        doc3 = "There are currently two builtin set types, set and frozenset"
        inary.search.init(['test'], ['en'])
        inary.search.add_doc(
            'test',
            'en',
            1,
            doc1,
            repo=db.itembyrepo.installed)
        inary.search.add_doc(
            'test',
            'en',
            2,
            doc2,
            repo=db.itembyrepo.installed)
        inary.search.add_doc(
            'test',
            'en',
            3,
            doc3,
            repo=db.itembyrepo.installed)
        q1 = inary.search.query(
            'test', 'en', ['set'], repo=db.itembyrepo.alldb)
        self.assertEqual(q1, set([1, 3]))
        q2 = inary.search.query(
            'test', 'en', [
                'an', 'collection'], repo=db.itembyrepo.alldb)
        self.assertEqual(q2, set([1, 2]))
        inary.search.finalize()

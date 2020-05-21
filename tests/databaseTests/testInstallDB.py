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


import inary
import inary.data
import inary.db
import unittest
from . import testcase


class InstallDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)

        self.installdb = inary.db.installdb.InstallDB()

    def tearDown(self):
        inary.api.remove(["timezone", "time", "acl", "attr"])

    def testGetPackage(self):
        inary.api.install(["timezone"])
        idb = inary.db.installdb.InstallDB()
        pkg = idb.get_package("timezone")
        self.assertEqual(type(pkg), inary.data.metadata.Package)
        self.assertEqual(pkg.name, "timezone")

    def testHasPackage(self):
        inary.api.install(["timezone"])
        self.installdb = inary.db.installdb.InstallDB()
        self.assertFalse(self.installdb.has_package("flipfloo"))
        self.assertTrue(self.installdb.has_package("timezone"))

    def testListInstalled(self):
        inary.api.install(["timezone", "time"])
        self.installdb = inary.db.installdb.InstallDB()
        self.assertEqual(set(self.installdb.list_installed()),
                         set(["timezone", "time"]))

    def testGetVersion(self):
        inary.api.install(["timezone"])
        self.installdb = inary.db.installdb.InstallDB()
        version, release, build = self.installdb.get_version("timezone")
        self.assertEqual(version, "2018e")
        self.assertEqual(release, "1")
        self.assertEqual(build, None)

    def testGetFiles(self):
        inary.api.install(["timezone"])
        self.installdb = inary.db.installdb.InstallDB()
        files = self.installdb.get_files("timezone")
        self.assertIn("usr/share/zoneinfo/Portugal",
                      [x.path for x in files.list])
        self.assertNotIn("usr/bin", [x.path for x in files.list])

    def testGetInfo(self):
        inary.api.install(["timezone"])
        idb = inary.db.installdb.InstallDB()
        info = idb.get_info("timezone")
        self.assertTrue(isinstance(info, inary.db.installdb.InstallInfo))
        self.assertEqual(info.version, "2018e")

    def testGetReverseDependencies(self):
        inary.api.install(["acl"])
        self.installdb = inary.db.installdb.InstallDB()
        revdeps = self.installdb.get_rev_deps("acl")
        self.assertIn(set(["attr"]), set(map(lambda x: x[0], revdeps)))

    def testAddRemovePackage(self):
        inary.api.install(["time"])
        self.installdb = inary.db.installdb.InstallDB()
        self.assertTrue(self.installdb.has_package("time"))
        self.assertFalse(self.installdb.has_package("timezone"))
        inary.api.install(["timezone"])
        self.installdb = inary.db.installdb.InstallDB()
        self.assertTrue(self.installdb.has_package("time"))
        self.assertTrue(self.installdb.has_package("timezone"))

    def testMarkListPending(self):
        self.skipTest(reason="")

    def testClearPending(self):
        self.skipTest(reason="")

    def testSearchPackage(self):
        self.installdb = inary.db.installdb.InstallDB()
        self.assertFalse(self.installdb.has_package("timezone"))
        self.assertFalse(self.installdb.search_package(["timezone"]))
        inary.api.install(["timezone"])
        self.installdb = inary.db.installdb.InstallDB()
        self.assertEqual(self.installdb.search_package(
            ["t", "ime", "zone"]), ["timezone"])

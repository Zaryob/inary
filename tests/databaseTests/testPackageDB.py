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
import inary


class PackageDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)

        self.packagedb = inary.db.packagedb.PackageDB()

    def testGetPackage(self):
        pkg = self.packagedb.get_package("bash", "core-binary")
        self.assertEqual(pkg.name, "bash")

        pkg = self.packagedb.get_package("grep", "core-src")
        self.assertEqual(pkg.name, "grep")

        pkg = self.packagedb.get_package("expat")
        self.assertEqual(pkg.name, "expat")

    def testHasPackage(self):
        self.assertTrue(self.packagedb.has_package("tar", "core-binary"))
        self.assertFalse(self.packagedb.has_package("tar", "core-src"))
        self.assertTrue(self.packagedb.has_package("zlib"))

    def testGetVersion(self):
        version, release, build = self.packagedb.get_version(
            "bash", "core-binary")
        self.assertEqual(version, "5.0")
        self.assertEqual(release, "1")

    def testWhichRepo(self):
        self.assertEqual(self.packagedb.which_repo("bash"), "core-binary")

    def testGetPackageAndRepository(self):
        pkg, repo = self.packagedb.get_package_repo("gcc")
        self.assertEqual(pkg.name, "gcc")
        self.assertEqual(repo, "core-binary")

    def testGetObsoletes(self):
        self.assertEqual(self.packagedb.get_obsoletes(), [])

    def testGetReverseDependencies(self):
        pkg, dep = self.packagedb.get_rev_deps("bash")[0]
        assert pkg == "bash-dbginfo"
        assert str(dep) == "bash release 1"

    def testGetReplaces(self):
        # FIXME: update createrepo.py to generate replaces
        assert not self.packagedb.get_replaces()

    def testListPackages(self):
        self.assertIn("expat", self.packagedb.list_packages("core-binary"))

    def testSearchPackage(self):
        packages = self.packagedb.search_package(["osd", "doc"])
        self.assertIn('biosdevname-docs', packages)

        packages = self.packagedb.search_package(
            ["32bit", "bus"], repo="core-binary")
        self.assertIn('dbus-32bit', packages)

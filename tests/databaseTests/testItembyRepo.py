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

import inary.db.itembyrepo


class TestDB:
    def __init__(self):
        self.packages = {}
        self.obsoletes = {}

        self.packages["repo1"] = {"aggdraw": "package aggdraw",
                                  "acpica": "package acpica"}
        self.packages["repo2"] = {"kdiff3": "package kdiff3",
                                  "kmess": "package kmess"}

        self.obsoletes["repo1"] = ["wengophone", "rar"]
        self.obsoletes["repo2"] = ["xara"]

        self.tdb = inary.db.itembyrepo.ItemByRepo(self.packages)
        self.odb = inary.db.itembyrepo.ItemByRepo(self.obsoletes)

        # original item_repos in ItemByRepo uses repodb.list_repos
        def item_repos(repo=None):
            repos = ["repo1", "repo2"]
            if repo:
                repos = [repo]
            return repos

        self.tdb.item_repos = item_repos
        self.odb.item_repos = item_repos


class ItemByRepoTestCase(testcase.TestCase):

    testdb = TestDB()

    def testHasRepository(self):
        self.assertTrue(self.testdb.tdb.has_repo("repo1"))
        self.assertTrue(self.testdb.tdb.has_repo("repo2"))
        self.assertFalse(self.testdb.tdb.has_repo("hedehodo"))

    def testHasItem(self):
        self.assertTrue(self.testdb.tdb.has_item("kdiff3", "repo2"))
        self.assertFalse(self.testdb.tdb.has_item("kdiff3", "repo1"))
        self.assertTrue(self.testdb.tdb.has_item("acpica"))

    def testWhichRepo(self):
        self.assertEqual(self.testdb.tdb.which_repo("aggdraw"), "repo1")
        self.assertEqual(self.testdb.tdb.which_repo("kmess"), "repo2")

    def testGetItemAndRepository(self):
        pkg, repo = self.testdb.tdb.get_item_repo("acpica")
        self.assertEqual(pkg, "package acpica")
        self.assertEqual(repo, "repo1")

        pkg, repo = self.testdb.tdb.get_item_repo("kmess")
        self.assertEqual(pkg, "package kmess")
        self.assertEqual(repo, "repo2")

    def testItemRepos(self):
        db = inary.db.itembyrepo.ItemByRepo({})
        self.assertEqual(db.item_repos("caracal"), ["caracal"])
        # repos were created by testcase.py
        self.assertEqual(db.item_repos(), ['core-src', 'core-binary'])

    def testGetItem(self):
        self.assertEqual(self.testdb.tdb.get_item("acpica"), "package acpica")
        self.assertEqual(self.testdb.tdb.get_item("kmess"), "package kmess")

    def testGetItemOfRepository(self):
        self.assertEqual(
            self.testdb.tdb.get_item(
                "acpica",
                "repo1"),
            "package acpica")
        self.assertEqual(
            self.testdb.tdb.get_item(
                "kmess",
                "repo2"),
            "package kmess")

    def testGetItemKeys(self):
        self.assertEqual(set(self.testdb.tdb.get_item_keys(
            "repo1")), set(["aggdraw", "acpica"]))
        self.assertEqual(set(self.testdb.tdb.get_item_keys(
            "repo2")), set(["kdiff3", "kmess"]))
        self.assertEqual(set(self.testdb.tdb.get_item_keys()),
                         set(["kdiff3", "kmess", "aggdraw", "acpica"]))

    def testGetListItem(self):
        self.assertEqual(set(self.testdb.odb.get_list_item(
            "repo1")), set(['rar', 'wengophone']))
        self.assertEqual(
            set(self.testdb.odb.get_list_item("repo2")), set(['xara']))
        self.assertEqual(set(self.testdb.odb.get_list_item()),
                         set(['rar', 'xara', 'wengophone']))

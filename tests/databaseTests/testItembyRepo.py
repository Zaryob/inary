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

from . import testcase

import inary.db.itembyrepo

class TestDB:
    def __init__(self):
        self.packages = {}
        self.obsoletes = {}

        self.packages["repo1"] = {"aggdraw":"package aggdraw",
                                        "acpica":"package acpica"}
        self.packages["repo2"] = {"kdiff3":"package kdiff3",
                                         "kmess":"package kmess"}

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
        assert self.testdb.tdb.has_repo("repo1")
        assert self.testdb.tdb.has_repo("repo2")
        assert not self.testdb.tdb.has_repo("hedehodo")

    def testHasItem(self):
        assert self.testdb.tdb.has_item("kdiff3", "repo2")
        assert not self.testdb.tdb.has_item("kdiff3", "repo1")
        assert self.testdb.tdb.has_item("acpica")

    def testWhichRepo(self):
        assert self.testdb.tdb.which_repo("aggdraw") == "repo1"
        assert self.testdb.tdb.which_repo("kmess") == "repo2"

    def testGetItemAndRepository(self):
        pkg, repo = self.testdb.tdb.get_item_repo("acpica")
        assert pkg == "package acpica"
        assert repo == "repo1"

        pkg, repo = self.testdb.tdb.get_item_repo("kmess")
        assert pkg == "package kmess"
        assert repo == "repo2"

    def testItemRepos(self):
        db = inary.db.itembyrepo.ItemByRepo({})
        assert db.item_repos("caracal") == ["caracal"]
        # repos were created by testcase.py
        assert db.item_repos() == ['repo1', 'repo2', 'repo1-src']

    def testGetItem(self):
        assert self.testdb.tdb.get_item("acpica") == "package acpica"
        assert self.testdb.tdb.get_item("kmess") == "package kmess"

    def testGetItemOfRepository(self):
        assert self.testdb.tdb.get_item("acpica", "repo1") == "package acpica"
        assert self.testdb.tdb.get_item("kmess", "repo2") == "package kmess"

    def testGetItemKeys(self):
        assert set(self.testdb.tdb.get_item_keys("repo1")) == set(["aggdraw", "acpica"])
        assert set(self.testdb.tdb.get_item_keys("repo2")) == set(["kdiff3", "kmess"])
        assert set(self.testdb.tdb.get_item_keys()) == set(["kdiff3", "kmess", "aggdraw", "acpica"])

    def testGetListItem(self):
        assert set(self.testdb.odb.get_list_item("repo1")) == set(['rar', 'wengophone'])
        assert set(self.testdb.odb.get_list_item("repo2")) == set(['xara'])
        assert set(self.testdb.odb.get_list_item()) == set(['rar', 'xara', 'wengophone'])

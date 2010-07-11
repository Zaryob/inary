# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2010, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import testcase
import pisi.db.itembyrepo

class TestDB:
    def __init__(self):
        self.packages = {}
        self.obsoletes = {}

        self.packages["pardus-2007"] = {"aggdraw":"package aggdraw",
                                        "acpica":"package acpica"}
        self.packages["contrib-2007"] = {"kdiff3":"package kdiff3",
                                         "kmess":"package kmess"}

        self.obsoletes["pardus-2007"] = ["wengophone", "rar"]
        self.obsoletes["contrib-2007"] = ["xara"]

        self.tdb = pisi.db.itembyrepo.ItemByRepo(self.packages)
        self.odb = pisi.db.itembyrepo.ItemByRepo(self.obsoletes)

        # original item_repos in ItemByRepo uses repodb.list_repos
        def item_repos(repo=None):
            repos = ["pardus-2007", "contrib-2007"]
            if repo:
                repos = [repo]
            return repos
        
        self.tdb.item_repos = item_repos
        self.odb.item_repos = item_repos

class ItemByRepoTestCase(testcase.TestCase):

    testdb = TestDB()

    def testHasRepository(self):
        assert self.testdb.tdb.has_repo("pardus-2007")
        assert self.testdb.tdb.has_repo("contrib-2007")
        assert not self.testdb.tdb.has_repo("hedehodo")

    def testHasItem(self):
        assert self.testdb.tdb.has_item("kdiff3", "contrib-2007")
        assert not self.testdb.tdb.has_item("kdiff3", "pardus-2007")
        assert self.testdb.tdb.has_item("acpica")

    def testWhichRepo(self):
        assert self.testdb.tdb.which_repo("aggdraw") == "pardus-2007"
        assert self.testdb.tdb.which_repo("kmess") == "contrib-2007"

    def testGetItemAndRepository(self):
        pkg, repo = self.testdb.tdb.get_item_repo("acpica")
        assert pkg == "package acpica"
        assert repo == "pardus-2007"

        pkg, repo = self.testdb.tdb.get_item_repo("kmess")
        assert pkg == "package kmess"
        assert repo == "contrib-2007"

    def testItemRepos(self):
        db = pisi.db.itembyrepo.ItemByRepo({})
        assert db.item_repos("caracal") == ["caracal"]
        # repos were created by testcase.py
        assert db.item_repos() == ['pardus-2007', 'contrib-2007', 'pardus-2007-src']

    def testGetItem(self):
        assert self.testdb.tdb.get_item("acpica") == "package acpica"
        assert self.testdb.tdb.get_item("kmess") == "package kmess"

    def testGetItemOfRepository(self):
        assert self.testdb.tdb.get_item("acpica", "pardus-2007") == "package acpica"
        assert self.testdb.tdb.get_item("kmess", "contrib-2007") == "package kmess"

    def testGetItemKeys(self):
        assert set(self.testdb.tdb.get_item_keys("pardus-2007")) == set(["aggdraw", "acpica"])
        assert set(self.testdb.tdb.get_item_keys("contrib-2007")) == set(["kdiff3", "kmess"])
        assert set(self.testdb.tdb.get_item_keys()) == set(["kdiff3", "kmess", "aggdraw", "acpica"])

    def testGetListItem(self):
        assert set(self.testdb.odb.get_list_item("pardus-2007")) == set(['rar', 'wengophone'])
        assert set(self.testdb.odb.get_list_item("contrib-2007")) == set(['xara'])
        assert set(self.testdb.odb.get_list_item()) == set(['rar', 'xara', 'wengophone'])

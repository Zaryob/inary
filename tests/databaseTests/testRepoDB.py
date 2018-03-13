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
import inary

class RepoDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.repodb = inary.db.repodb.RepoDB()

    def testAddRemoveRepo(self):
        assert "repo2-src" not in self.repodb.list_repos()
        repo = inary.db.repodb.Repo(inary.uri.URI("../repos/repo2/inary-index.xml"))
        self.repodb.add_repo("repo2-src", repo)
        assert "repo2-src" in self.repodb.list_repos()
        self.repodb.remove_repo("repo2-src")
        assert "repo2" in self.repodb.list_repos()
        assert "repo1" in self.repodb.list_repos()
        assert "repo2-src" not in self.repodb.list_repos()

    def testAddRemoveCycle(self):
        for r in range(30):
            assert "test-repo" not in self.repodb.list_repos()
            repo = inary.db.repodb.Repo(inary.uri.URI("http://test-repo/inary-index.xml"))
            self.repodb.add_repo("test-repo", repo)
            assert "test-repo" in self.repodb.list_repos()
            self.repodb.remove_repo("test-repo")

        assert "test-repo" not in self.repodb.list_repos()

    def testListRepos(self):
        assert set(self.repodb.list_repos()) == set(['repo1', 'repo2', 'repo1-src'])

    def testGetSourceRepos(self):
        assert set(self.repodb.get_source_repos()) == set(['repo1-src'])

    def testGetBinaryRepos(self):
        assert set(self.repodb.get_binary_repos()) == set(['repo1', 'repo2'])

    def testGetRepo(self):
        repo = self.repodb.get_repo("repo1")
        uri = repo.indexuri
        assert uri.get_uri() == "../repos/repo1-bin/inary-index.xml"

    def testRepoOrder(self):
        repoorder = inary.db.repodb.RepoOrder()
        assert repoorder.get_order() == ['repo1', 'repo2', 'repo1-src']

        repoorder.add("test-repo", "http://test-repo/inary-index.xml")
        assert repoorder.get_order() == ['repo1', 'repo2', 'repo1-src', 'test-repo']

        repoorder.remove("test-repo")
        assert repoorder.get_order() == ['repo1', 'repo2', 'repo1-src']

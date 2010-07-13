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
import pisi

class RepoDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.repodb = pisi.db.repodb.RepoDB()

    def testAddRemoveRepo(self):
        assert "contrib-2007-src" not in self.repodb.list_repos()
        repo = pisi.db.repodb.Repo(pisi.uri.URI("repos/contrib-2007/pisi-index.xml"))
        self.repodb.add_repo("contrib-2007-src", repo)
        assert "contrib-2007-src" in self.repodb.list_repos()
        self.repodb.remove_repo("contrib-2007-src")
        assert "contrib-2007" in self.repodb.list_repos()
        assert "pardus-2007" in self.repodb.list_repos()
        assert "contrib-2007-src" not in self.repodb.list_repos()

    def testAddRemoveCycle(self):
        for r in range(30):
            assert "test-repo" not in self.repodb.list_repos()
            repo = pisi.db.repodb.Repo(pisi.uri.URI("http://test-repo/pisi-index.xml"))
            self.repodb.add_repo("test-repo", repo)
            assert "test-repo" in self.repodb.list_repos()
            self.repodb.remove_repo("test-repo")

        assert "test-repo" not in self.repodb.list_repos()

    def testListRepos(self):
        assert set(self.repodb.list_repos()) == set(['pardus-2007', 'contrib-2007', 'pardus-2007-src'])

    def testGetSourceRepos(self):
        assert set(self.repodb.get_source_repos()) == set(['pardus-2007-src'])

    def testGetBinaryRepos(self):
        assert set(self.repodb.get_binary_repos()) == set(['pardus-2007', 'contrib-2007'])

    def testGetRepo(self):
        repo = self.repodb.get_repo("pardus-2007")
        uri = repo.indexuri
        assert uri.get_uri() == "repos/pardus-2007-bin/pisi-index.xml"

    def testRepoOrder(self):
        repoorder = pisi.db.repodb.RepoOrder()
        assert repoorder.get_order() == ['pardus-2007', 'contrib-2007', 'pardus-2007-src']

        repoorder.add("test-repo", "http://test-repo/pisi-index.xml")
        assert repoorder.get_order() == ['pardus-2007', 'contrib-2007', 'pardus-2007-src', 'test-repo']

        repoorder.remove("test-repo")
        assert repoorder.get_order() == ['pardus-2007', 'contrib-2007', 'pardus-2007-src']

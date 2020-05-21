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
import unittest
from . import testcase


class RepoDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)

        self.repodb = inary.db.repodb.RepoDB()

    def testAddRemoveRepo(self):
        self.assertNotIn("repo2-src", self.repodb.list_repos())
        repo = inary.db.repodb.Repo(
            inary.uri.URI("repos/repo2/inary-index.xml"))
        self.repodb.add_repo("repo2-src", repo)
        self.assertIn("repo2-src", self.repodb.list_repos())
        self.repodb.remove_repo("repo2-src")
        self.assertIn("core-src", self.repodb.list_repos())
        self.assertIn("core-binary", self.repodb.list_repos())
        self.assertNotIn("repo2-src", self.repodb.list_repos())

    def testAddRemoveCycle(self):
        for r in range(30):
            self.assertNotIn("test-repo", self.repodb.list_repos())
            repo = inary.db.repodb.Repo(
                inary.uri.URI("http://test-repo/inary-index.xml"))
            self.repodb.add_repo("test-repo", repo)
            self.assertIn("test-repo", self.repodb.list_repos())
            self.repodb.remove_repo("test-repo")

        self.assertNotIn("test-repo", self.repodb.list_repos())

    def testListRepos(self):
        self.assertEqual(set(self.repodb.list_repos()),
                         set(['core-src', 'core-binary']))

    def testGetSourceRepos(self):
        self.assertEqual(set(self.repodb.get_source_repos()),
                         set(['core-src']))

    def testGetBinaryRepos(self):
        self.assertEqual(set(self.repodb.get_binary_repos()),
                         set(['core-binary']))

    def testGetRepo(self):
        repo = self.repodb.get_repo("core-src")
        uri = repo.indexuri
        self.assertEqual(
            uri.get_uri(),
            "http://127.0.0.1/SulinRepository/inary-index.xml")

    def testRepoOrder(self):
        repoorder = inary.db.repodb.RepoOrder()
        self.assertEqual(repoorder.get_order(), ['core-src', 'core-binary'])

        repoorder.add("test-repo", "http://test-repo/inary-index.xml")
        self.assertEqual(
            repoorder.get_order(), [
                'core-src', 'core-binary', 'test-repo'])

        repoorder.remove("test-repo")
        self.assertEqual(repoorder.get_order(), ['core-src', 'core-binary'])

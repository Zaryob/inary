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
        pkg = self.packagedb.get_package("ncftp", "repo1")
        assert pkg.name == "ncftp"

        pkg = self.packagedb.get_package("lynx", "repo2")
        assert pkg.name == "lynx"

        pkg = self.packagedb.get_package("cpulimit")
        assert pkg.name == "cpulimit"

    def testHasPackage(self):
        assert self.packagedb.has_package("ncftp", "repo1")
        assert not self.packagedb.has_package("ncftp", "repo2")
        assert self.packagedb.has_package("lynx")

    def testGetVersion(self):
        version, release, build = self.packagedb.get_version("lynx", "repo2")
        assert version == "0.3"
        assert release == "1"

    def testWhichRepo(self):
        assert self.packagedb.which_repo("lynx") == "repo2"

    def testGetPackageAndRepository(self):
        pkg, repo = self.packagedb.get_package_repo("cpulimit")
        assert pkg.name == "cpulimit"
        assert repo == "repo2"

    def testGetObsoletes(self):
        assert set(self.packagedb.get_obsoletes("repo1")) == set(["wengophone", "rar"])
        assert set(self.packagedb.get_obsoletes("repo2")) == set(["xara"])
        assert set(self.packagedb.get_obsoletes()) == set(["wengophone", "rar", "xara"])

    def testGetReverseDependencies(self):
        pkg, dep = self.packagedb.get_rev_deps("openssl")[0]
        assert pkg == "curl"
        assert str(dep) == "openssl"

    def testGetReplaces(self):
        # FIXME: update createrepo.py to generate replaces
        assert not self.packagedb.get_replaces()

    def testListPackages(self):
        assert set(self.packagedb.list_packages("repo1")) == set(['nfdump', 'ethtool', 'ncftp',
                                                                        'libidn', 'zlib', 'db4', 'openssl',
                                                                        'jpeg', 'pam', 'shadow', 'bogofilter',
                                                                        'curl', 'gsl', 'bash', 'cracklib'])

        assert set(self.packagedb.list_packages("repo2")) == set(['libpcap', 'ctorrent', 'lft', 'lynx',
                                                                         'iat', 'cpulimit', 'rpl'])

    def testSearchPackage(self):
        packages = self.packagedb.search_package(["bogo", "filter"])
        packages = ["bogofilter"]

        packages = self.packagedb.search_package(["cpu", "limit"], repo="repo2")
        packages = ["cpulimit"]

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

class PackageDBTestCase(testcase.TestCase):
    
    def setUp(self):
        testcase.TestCase.setUp(self)
        self.packagedb = inary.db.packagedb.PackageDB()

    def testGetPackage(self):
        pkg = self.packagedb.get_package("tidy", "repo1")
        assert pkg.name == "tidy"

        pkg = self.packagedb.get_package("most", "repo2")
        assert pkg.name == "most"

        pkg = self.packagedb.get_package("lsof")
        assert pkg.name == "lsof"

    def testHasPackage(self):
        assert self.packagedb.has_package("tidy", "repo1")
        assert not self.packagedb.has_package("most", "repo2")
        assert self.packagedb.has_package("lsof")

    def testGetVersion(self):
        version, release, build = self.packagedb.get_version("most", "repo2")
        assert version == "5,1_pre6"
        assert release == "2"

    def testWhichRepo(self):
        assert self.packagedb.which_repo("lsof") == "repo2"

    def testGetPackageAndRepository(self):
        pkg, repo = self.packagedb.get_package_repo("lsof")
        assert pkg.name == "lsof"
        assert repo == "repo2"

    def testGetObsoletes(self):
        assert set(self.packagedb.get_obsoletes("repo1")) == set(["live-system", "live-streams"])
        assert set(self.packagedb.get_obsoletes("repo2")) == set(["live-area"])
        assert set(self.packagedb.get_obsoletes()) == set(["live-system", "live-streams", "live-area"])

    def testGetReverseDependencies(self):
        pkg, dep = self.packagedb.get_rev_deps("openssl")[0]
        assert pkg == "zlib"
        assert str(dep) == "openssl"

    def testGetReplaces(self):
        # FIXME: update createrepo.py to generate replaces
        assert not self.packagedb.get_replaces()

    def testListPackages(self):
        assert set(self.packagedb.list_packages("repo1")) == set(['liblouis','jpeg','jpeg-devel','jpeg-32bit',
                                                                  'tidy', 'tidy-devel', 'vlock', 'pv', 'dialog',
                                                                  'zlib','zlib-devel', 'zlib-32bit', 'minizip',
                                                                  'minizip-devel', 'ncurses', 'ncurses-devel',
                                                                  'ncurses-32bit', 'bash', 'ca-certificates',
                                                                  'openssl', 'openssl-devel', 'openssl-32bit',
                                                                  'run-parts', 'xorg-util', 'gnuconfig', 'uif2iso'])

        assert set(self.packagedb.list_packages("repo2")) == set(['lsof', 'most', 'dialog', 'inxi'])

    def testSearchPackage(self):
        packages = self.packagedb.search_package(["dial"])
        assert packages == ["dialog"]

        packages = self.packagedb.search_package(["devel"], repo="repo1")
        assert packages == set(["openssl-devel","tidy-devel", "ncurses-devel", "jpeg-devel", "zlib-devel"])

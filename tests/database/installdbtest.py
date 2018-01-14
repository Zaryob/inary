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

from . import testcase
import inary

class InstallDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.installdb = inary.db.installdb.InstallDB()

    def tearDown(self):
        inary.api.remove(["ctorrent", "ethtool"])

    def testGetPackage(self):
        inary.api.install(["ethtool"])
        idb = inary.db.installdb.InstallDB()
        pkg = idb.get_package("ethtool")
        assert type(pkg) == inary.metadata.Package
        assert pkg.name == "ethtool"

    def testHasPackage(self):
        inary.api.install(["ethtool"])
        self.installdb = inary.db.installdb.InstallDB()
        assert not self.installdb.has_package("hedehodo")
        assert self.installdb.has_package("ethtool")

    def testListInstalled(self):
        inary.api.install(["ethtool"])
        self.installdb = inary.db.installdb.InstallDB()
        assert set(self.installdb.list_installed()) == set(['zlib', 'pam', 'shadow', 
                                                            'jpeg', 'libidn', 'db4', 
                                                            'cracklib', 'openssl', 
                                                            'curl', 'bash', 'ethtool'])

    def testGetVersion(self):
        inary.api.install(["ethtool"])
        self.installdb = inary.db.installdb.InstallDB()
        version, release, build = self.installdb.get_version("zlib")
        assert version == "0.3"
        assert release == "1"
        assert build == None

    def testGetFiles(self):
        inary.api.install(["ethtool"])
        self.installdb = inary.db.installdb.InstallDB()
        files = self.installdb.get_files("ethtool")
        assert files.list[0].path == "usr/bin/ethtool"

    def testGetInfo(self):
        inary.api.install(["ethtool"])
        idb = inary.db.installdb.InstallDB()
        info = idb.get_info("ethtool")
        self.assertTrue(isinstance(info, inary.db.installdb.InstallInfo))
        self.assertEqual(info.version, "0.3")

    def testGetReverseDependencies(self):
        inary.api.install(["ethtool"])
        inary.api.install(["ctorrent"])
        self.installdb = inary.db.installdb.InstallDB()
        revdeps = self.installdb.get_rev_deps("openssl")
        assert set(["ctorrent", "curl"]) == set([x[0] for x in revdeps])

    def testAddRemovePackage(self):
        inary.api.install(["ctorrent"])
        self.installdb = inary.db.installdb.InstallDB()
        assert self.installdb.has_package("ctorrent")
        assert not self.installdb.has_package("ethtool")
        inary.api.install(["ethtool"])
        self.installdb = inary.db.installdb.InstallDB()
        assert self.installdb.has_package("ctorrent")
        assert self.installdb.has_package("ethtool")

    def testMarkListPending(self):
        inary.api.set_scom(False)
        assert not self.installdb.has_package("ethtool")
        inary.api.install(["ethtool"])
        assert "ethtool" in self.installdb.list_pending()
        inary.api.remove(["ethtool"])
        assert "ethtool" not in self.installdb.list_pending()
        inary.api.set_scom(True)

    def testClearPending(self):
        inary.api.set_scom(False)
        assert not self.installdb.has_package("ethtool")
        inary.api.install(["ethtool"])
        assert "ethtool" in self.installdb.list_pending()
        self.installdb.clear_pending("ethtool")
        assert "ethtool" not in self.installdb.list_pending()
        inary.api.remove(["ethtool"])
        assert "ethtool" not in self.installdb.list_pending()
        inary.api.set_scom(True)

    def testSearchPackage(self):
        self.installdb = inary.db.installdb.InstallDB()
        assert not self.installdb.has_package("ethtool")
        assert not self.installdb.search_package(["ethtool"])
        inary.api.install(["ethtool"])
        self.installdb = inary.db.installdb.InstallDB()
        assert self.installdb.search_package(["et", "tool", "h"]) == ["ethtool"]

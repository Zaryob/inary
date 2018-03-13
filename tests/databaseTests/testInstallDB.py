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

class InstallDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.installdb = inary.db.installdb.InstallDB()

    def tearDown(self):
        inary.api.remove(["dialog", "pv"])

    def testGetPackage(self):
        inary.api.install(["dialog"])
        idb = inary.db.installdb.InstallDB()
        pkg = idb.get_package("dialog")
        assert type(pkg) == inary.metadata.Package
        assert pkg.name == "dialog"

    def testHasPackage(self):
        inary.api.install(["dialog"])
        self.installdb = inary.db.installdb.InstallDB()
        assert not self.installdb.has_package("flipfloo")
        assert self.installdb.has_package("dialog")

    def testListInstalled(self):
        inary.api.install(["openssl"])
        self.installdb = inary.db.installdb.InstallDB()
        assert set(self.installdb.list_installed()) == set(['zlib', 'ca-certificates',
                                                            'run-parts', 'openssl'])

    def testGetVersion(self):
        inary.api.install(["dialog"])
        self.installdb = inary.db.installdb.InstallDB()
        version, release, build = self.installdb.get_version("zlib")
        assert version == "1.1_20100428"
        assert release == "10"
        assert build == None

    def testGetFiles(self):
        inary.api.install(["bash"])
        self.installdb = inary.db.installdb.InstallDB()
        files = self.installdb.get_files("bash")
        assert files.list[0].path == "bin/bash"

    def testGetInfo(self):
        inary.api.install(["dialog"])
        idb = inary.db.installdb.InstallDB()
        info = idb.get_info("dialog")
        self.assertTrue(isinstance(info, inary.db.installdb.InstallInfo))
        self.assertEqual(info.version, "1.1_20100428")

    #FIXME: Yuksek ihtimal calismayacak
    def testGetReverseDependencies(self):
        inary.api.install(["pv"])
        inary.api.install(["dialog"])
        self.installdb = inary.db.installdb.InstallDB()
        revdeps = self.installdb.get_rev_deps("openssl")
        assert set(["pv", "dialog"]) == set([x[0] for x in revdeps])

    def testAddRemovePackage(self):
        inary.api.install(["pv"])
        self.installdb = inary.db.installdb.InstallDB()
        assert self.installdb.has_package("pv")
        assert not self.installdb.has_package("dialog")
        inary.api.install(["dialog"])
        self.installdb = inary.db.installdb.InstallDB()
        assert self.installdb.has_package("pv")
        assert self.installdb.has_package("dialog")

    def testMarkListPending(self):
        inary.api.set_scom(False)
        assert not self.installdb.has_package("openssl")
        inary.api.install(["openssl"])
        assert "openssl" in self.installdb.list_pending()
        inary.api.remove(["openssl"])
        assert "openssl" not in self.installdb.list_pending()
        inary.api.set_scom(True)

    def testClearPending(self):
        inary.api.set_scom(False)
        assert not self.installdb.has_package("openssl")
        inary.api.install(["openssl"])
        assert "openssl" in self.installdb.list_pending()
        self.installdb.clear_pending("openssl")
        assert "openssl" not in self.installdb.list_pending()
        inary.api.remove(["openssl"])
        assert "openssl" not in self.installdb.list_pending()
        inary.api.set_scom(True)

    def testSearchPackage(self):
        self.installdb = inary.db.installdb.InstallDB()
        assert not self.installdb.has_package("tidy")
        assert not self.installdb.search_package(["tidy"])
        inary.api.install(["tidy"])
        self.installdb = inary.db.installdb.InstallDB()
        assert self.installdb.search_package(["tid", "idy", "t"]) == ["tidy"]

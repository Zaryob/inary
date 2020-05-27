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


class SourceDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.sourcedb = inary.db.sourcedb.SourceDB()

    def testListSources(self):
        self.skipTest(reason="")

    def testHasSpec(self):
        assert self.sourcedb.has_spec("openssl")
        assert not self.sourcedb.has_spec("hedehodo")

    def testGetSpec(self):
        spec = self.sourcedb.get_spec("zlib")
        assert spec.source.name == "zlib"
        assert spec.source.partOf == "system.base"

    def testGetSpecOfRepository(self):
        spec = self.sourcedb.get_spec("xz", "core-src")
        assert spec.source.name == "xz"
        assert spec.source.partOf == "system.base"

    def testGetSpecAndRepository(self):
        spec, repo = self.sourcedb.get_spec_repo("openssl")
        assert spec.source.name == "openssl"
        assert spec.source.partOf == "system.base"
        assert repo == "core-src"

    def testGetSourceFromPackage(self):
        pkg = self.sourcedb.pkgtosrc("xz")
        assert pkg == "xz"

    def testSearchPackage(self):
        packages = self.sourcedb.search_spec(["open", "ssl"])
        assert set(["openssl"]) == set(packages)

        packages = self.sourcedb.search_spec(["xorg", "util"], repo="core-src")
        assert set(["xorg-util"]) == set(packages)

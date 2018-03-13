# -*- coding: utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

from . import testcase
import inary

class SourceDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)

        self.sourcedb = inary.db.sourcedb.SourceDB()


    def testListSources(self):
        assert set(self.sourcedb.list_sources()) == set(['bash', 'ca-certificates', 'dialog', 'gnuconfig', 
                                                         'zlib', 'pv', 'openssl', 'jpeg', 'liblouis', 'tidy',
                                                         'xorg-util', 'vlock', 'run-parts', 'ncurses', 'uif2iso' ])
    
    def testHasSpec(self):
        assert self.sourcedb.has_spec("bash")
        assert not self.sourcedb.has_spec("flict-floct")

    def testGetSpec(self):
        spec = self.sourcedb.get_spec("vlock")
        assert spec.source.name == "vlock"
        assert spec.source.partOf == "util"

    def testGetSpecOfRepository(self):
        spec = self.sourcedb.get_spec("dialog", "repo1")
        assert spec.source.name == "dialog"
        assert spec.source.partOf == "util"

    def testGetSpecAndRepository(self):
        spec, repo = self.sourcedb.get_spec_repo("pv")
        assert spec.source.name == "pv"
        assert spec.source.partOf == "util"
        assert repo == "repo1"

    def testGetSourceFromPackage(self):
        # FIXME: Add multi package from source to createrepo.py
        pkg = self.sourcedb.pkgtosrc("run-parts")
        assert pkg == "runparts"

    def testSearchPackage(self):
        packages = self.sourcedb.search_spec(["open", "ssl"])
        assert set(["openssl"]) == set(packages)

        packages = self.sourcedb.search_spec(["liblo", "!ouis"], repo="repo1")
        assert set(["liblouis"]) == set(packages)



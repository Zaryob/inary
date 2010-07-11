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

class SourceDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)

        self.sourcedb = pisi.db.sourcedb.SourceDB()


    def testListSources(self):
        assert set(self.sourcedb.list_sources()) == set(['ethtool', 'nfdump', 'shadow', 'libidn', 
                                                         'zlib', 'db4', 'openssl', 'jpeg', 'gsl', 
                                                         'curl', 'bogofilter', 'ncftp', 'pam', 
                                                         'bash', 'cracklib'])
    
    def testHasSpec(self):
        assert self.sourcedb.has_spec("ethtool")
        assert not self.sourcedb.has_spec("hedehodo")

    def testGetSpec(self):
        spec = self.sourcedb.get_spec("ethtool")
        assert spec.source.name == "ethtool"
        assert spec.source.partOf == "applications.network"

    def testGetSpecOfRepository(self):
        spec = self.sourcedb.get_spec("ethtool", "pardus-2007-src")
        assert spec.source.name == "ethtool"
        assert spec.source.partOf == "applications.network"

    def testGetSpecAndRepository(self):
        spec, repo = self.sourcedb.get_spec_repo("ethtool")
        assert spec.source.name == "ethtool"
        assert spec.source.partOf == "applications.network"
        assert repo == "pardus-2007-src"

    def testGetSourceFromPackage(self):
        # FIXME: Add multi package from source to createrepo.py
        pkg = self.sourcedb.pkgtosrc("cracklib")
        assert pkg == "cracklib"

    def testSearchPackage(self):
        packages = self.sourcedb.search_spec(["open", "ssl"])
        assert set(["openssl"]) == set(packages)

        packages = self.sourcedb.search_spec(["bogo", "filter"], repo="pardus-2007-src")
        assert set(["bogofilter"]) == set(packages)



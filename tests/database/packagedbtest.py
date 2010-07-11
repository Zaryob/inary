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

class PackageDBTestCase(testcase.TestCase):
    
    def setUp(self):
        testcase.TestCase.setUp(self)
        self.packagedb = pisi.db.packagedb.PackageDB()

    def testGetPackage(self):
        pkg = self.packagedb.get_package("ncftp", "pardus-2007")
        assert pkg.name == "ncftp"

        pkg = self.packagedb.get_package("lynx", "contrib-2007")
        assert pkg.name == "lynx"

        pkg = self.packagedb.get_package("cpulimit")
        assert pkg.name == "cpulimit"

    def testHasPackage(self):
        assert self.packagedb.has_package("ncftp", "pardus-2007")
        assert not self.packagedb.has_package("ncftp", "contrib-2007")
        assert self.packagedb.has_package("lynx")

    def testGetVersion(self):
        version, release, build = self.packagedb.get_version("lynx", "contrib-2007")
        assert version == "0.3"
        assert release == "1"

    def testWhichRepo(self):
        assert self.packagedb.which_repo("lynx") == "contrib-2007"

    def testGetPackageAndRepository(self):
        pkg, repo = self.packagedb.get_package_repo("cpulimit")
        assert pkg.name == "cpulimit"
        assert repo == "contrib-2007"

    def testGetObsoletes(self):
        assert set(self.packagedb.get_obsoletes("pardus-2007")) == set(["wengophone", "rar"])
        assert set(self.packagedb.get_obsoletes("contrib-2007")) == set(["xara"])
        assert set(self.packagedb.get_obsoletes()) == set(["wengophone", "rar", "xara"])

    def testGetReverseDependencies(self):
        pkg, dep = self.packagedb.get_rev_deps("openssl")[0]
        assert pkg == "curl"
        assert str(dep) == "openssl"

    def testGetReplaces(self):
        # FIXME: update createrepo.py to generate replaces
        assert not self.packagedb.get_replaces()

    def testListPackages(self):
        assert set(self.packagedb.list_packages("pardus-2007")) == set(['nfdump', 'ethtool', 'ncftp', 
                                                                        'libidn', 'zlib', 'db4', 'openssl', 
                                                                        'jpeg', 'pam', 'shadow', 'bogofilter', 
                                                                        'curl', 'gsl', 'bash', 'cracklib'])

        assert set(self.packagedb.list_packages("contrib-2007")) == set(['libpcap', 'ctorrent', 'lft', 'lynx', 
                                                                         'iat', 'cpulimit', 'rpl'])

    def testSearchPackage(self):
        packages = self.packagedb.search_package(["bogo", "filter"])
        packages = ["bogofilter"]

        packages = self.packagedb.search_package(["cpu", "limit"], repo="contrib-2007")
        packages = ["cpulimit"]

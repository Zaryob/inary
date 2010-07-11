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

class ComponentDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.componentdb = pisi.db.componentdb.ComponentDB()

    def testHasComponent(self):
        assert self.componentdb.has_component("system.base", "pardus-2007")
        assert not self.componentdb.has_component("hede.hodo", "pardus-2007")
        assert self.componentdb.has_component("applications.network", "contrib-2007")
        assert not self.componentdb.has_component("hede.hodo", "contrib-2007")
        assert self.componentdb.has_component("applications.network")

    def testListComponents(self):
        assert set(self.componentdb.list_components("pardus-2007")) == set(["system", "system.base", 
                                                                            "applications", "applications.network"])
        assert set(self.componentdb.list_components("contrib-2007")) == set(["applications", "applications.util",
                                                                             "applications.network"])
        assert set(self.componentdb.list_components()) == set(["system", "system.base", 
                                                               "applications", "applications.network",
                                                               "applications.util"])

    def testGetComponent(self):
        component = self.componentdb.get_component("applications.network")
        assert component.name == "applications.network"
        assert "ncftp" in component.packages
        assert "lynx" not in component.packages

        component = self.componentdb.get_component("applications.network", "contrib-2007")
        assert component.name == "applications.network"
        assert "lynx" in component.packages
        assert "ncftp" not in component.packages

    def testGetUnionComponent(self):
        component = self.componentdb.get_union_component("applications.network")
        assert component.name == "applications.network"
        assert "lynx" in component.packages
        assert "ncftp" in component.packages

    def testGetPackages(self):
        packages = self.componentdb.get_packages("applications.network")
        assert "ncftp" in packages
        assert "lynx" not in packages

        packages = self.componentdb.get_packages("applications.network", "contrib-2007")
        assert "lynx" in packages
        assert "ncftp" not in packages

        packages = self.componentdb.get_packages("applications", "contrib-2007", walk = True)
        assert "cpulimit" and "lynx" in packages
        assert "ncftp" not in packages

    def testGetUnionPackages(self):
        packages = self.componentdb.get_union_packages("applications.network")
        assert "ncftp" in packages
        assert "lynx" in packages
        assert "cpulimit" not in packages

        packages = self.componentdb.get_union_packages("applications", walk = True)
        assert "ncftp" and "lynx" and "cpulimit" in packages

    def testSearchComponent(self):
        packages = self.componentdb.search_component(["applic"])
        assert set(packages) == set(['applications', 'applications.network', 'applications.util'])

        packages = self.componentdb.search_component(["system", "base"], repo="pardus-2007")
        assert set(packages) == set(["system.base"])

        packages = self.componentdb.search_component(["system", "base"], repo="contrib-2007")
        assert not packages

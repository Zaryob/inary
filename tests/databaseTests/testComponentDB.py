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

class ComponentDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.componentdb = inary.db.componentdb.ComponentDB()

    def testHasComponent(self):
        assert self.componentdb.has_component("system.base", "repo1")
        assert not self.componentdb.has_component("floct.flict", "repo1")
        assert self.componentdb.has_component("util.misc", "repo2")
        assert not self.componentdb.has_component("floct.flict", "repo2")
        assert self.componentdb.has_component("multimedia.graphics")

    def testListComponents(self):
        assert set(self.componentdb.list_components("repo1")) == set(["system", "system.base",
                                                                      "system.devel", "util",
                                                                      "desktop", "desktop.accessibility",
                                                                      "multimedia", "multimedia.graphics"])
        assert set(self.componentdb.list_components("repo2")) == set(["system", "system.base",
                                                                      "util", "util.admin", "util.misc"])

    def testGetComponent(self):
        component = self.componentdb.get_component("system.base", "repo1")
        assert component.name == "system.base"
        assert "bash" in component.packages
        assert "gnuconfig" not in component.packages

        component = self.componentdb.get_component("util.misc", "repo2")
        assert component.name == "util"
        assert "dialog" in component.packages
        assert "jpeg" not in component.packages

    def testGetUnionComponent(self):
        component = self.componentdb.get_union_component("multimedia.graphics", "repo1")
        assert component.name == "multimedia.graphics"
        assert "jpeg" in component.packages
        assert "dialog" in component.packages

    def testGetPackages(self):
        packages = self.componentdb.get_packages("system.devel", "repo1")
        assert "xorg-util" in packages
        assert "dialog" not in packages

        packages = self.componentdb.get_packages("util.misc", "repo2")
        assert "dialog" in packages
        assert "jpeg" not in packages

        #Test Walking parameter
        packages = self.componentdb.get_packages("util", "repo2", walk = True)
        assert "lsof" and "inxi" in packages
        assert "ftp" not in packages

    def testGetUnionPackages(self):
        packages = self.componentdb.get_union_packages("util", "repo1")
        assert "dialog" in packages
        assert "tidy" in packages
        assert "cpulimit" not in packages

        packages = self.componentdb.get_union_packages("system", 'repo1', walk = True)
        assert "gnuconfig" and "ca-certificates" and "bash" in packages

    def testSearchComponent(self):
        packages = self.componentdb.search_component(["uti"])
        assert set(packages) == set(['util', 'util.admin', 'util.misc'])

        packages = self.componentdb.search_component(["system", "base"], repo="repo1")
        assert set(packages) == set(["system.base"])

        packages = self.componentdb.search_component(["system", "devel"], repo="repo2")
        assert not packages

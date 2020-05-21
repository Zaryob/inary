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


import inary
import inary.db
import unittest
from . import testcase


class ComponentDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.componentdb = inary.db.componentdb.ComponentDB()

    def testHasComponent(self):
        self.assertTrue(
            self.componentdb.has_component(
                "system.base",
                "core-binary"))
        self.assertFalse(
            self.componentdb.has_component(
                "floct.flict",
                "core-binary"))
        self.assertTrue(
            self.componentdb.has_component(
                "multimedia.graphics",
                "core-src"))
        self.assertFalse(
            self.componentdb.has_component(
                "floct.flict", "core-src"))
        self.assertTrue(self.componentdb.has_component(
            "programming.language.python"))

    def testListComponents(self):
        self.assertEqual(set(self.componentdb.list_components(repo="core-binary")), set(['util.shell', 'programming.environment.kdevelop',
                                                                                         'programming.environment.eclipse', 'system.devel',
                                                                                         'util.archive', 'programming.tool', 'office.docbook',
                                                                                         'multimedia', 'desktop', 'util.admin', 'x11',
                                                                                         'x11.library', 'programming.devel', 'util',
                                                                                         'util.crypt', 'hardware.disk', 'system.boot',
                                                                                         'hardware', 'system.pages', 'system.locale',
                                                                                         'tex.base', 'x11.util', 'office', 'system',
                                                                                         'desktop.font', 'system.base', 'programming.library',
                                                                                         'programming.environment.eric', 'tex',
                                                                                         'programming', 'programming.language.python',
                                                                                         'programming.environment', 'util.misc',
                                                                                         'multimedia.graphics', 'system.doc',
                                                                                         'programming.language', 'programming.docs']))

        if set(["applications", "applications.util", "applications.network"]) not in set(
                self.componentdb.list_components()):
            assert True
        else:
            assert False

    def testGetComponent(self):
        component = self.componentdb.get_component("system.base")
        self.assertEqual(component.name, "system.base")
        self.assertIn("expat", component.packages)
        self.assertNotIn("expat-devel", component.packages)

        component = self.componentdb.get_component(
            "util.admin", repo="core-binary")
        self.assertEqual(component.name, "util.admin")
        self.assertIn("libcap-ng-utils", component.packages)
        self.assertNotIn("ncftp", component.packages)

    def testGetUnionComponent(self):
        component = self.componentdb.get_union_component("system.locale")
        self.assertEqual(component.name, "system.locale")
        self.assertIn("glibc-locales-so", component.packages)
        self.assertNotIn("minizip", component.packages)

    def testGetPackages(self):
        packages = self.componentdb.get_packages("system.devel")
        self.assertIn("expat-devel", packages)
        self.assertNotIn("expat", packages)

        packages = self.componentdb.get_packages(
            "util.misc", repo="core-binary")
        self.assertIn("uuidd", packages)
        self.assertNotIn("ncftp", packages)

        packages = self.componentdb.get_packages("system.pages", walk=True)
        self.assertIn("autoconf-pages" and "autoconf-pages", packages)

    def testGetSources(self):
        packages = self.componentdb.get_sources("system.devel")
        self.assertIn("isl", packages)
        self.assertNotIn("ncftp", packages)

        packages = self.componentdb.get_sources(
            "system.devel", repo="core-binary")
        self.assertEqual([], packages)

        packages = self.componentdb.get_packages("system.devel", walk=True)
        self.assertIn("ppl" and "expat-devel", packages)

    def testGetUnionPackages(self):
        packages = self.componentdb.get_union_packages("programming.devel")
        self.assertIn('device-mapper-event-devel', packages)
        self.assertNotIn("ncftp", packages)

        packages = self.componentdb.get_union_packages(
            "system.pages", walk=True)
        assert "autoconf-pages" and "autoconf-pages" in packages

    def testSearchComponent(self):
        packages = self.componentdb.search_component(["yst"])
        self.assertIn('system.base', set(packages))
        self.assertNotIn('programming', set(packages))

        packages = self.componentdb.search_component(
            ["doc"], repo="core-binary")
        self.assertIn("system.doc", packages)

        packages = self.componentdb.search_component(
            ["til", "isc"], repo="core-binary")
        self.assertIn("util.misc", packages)

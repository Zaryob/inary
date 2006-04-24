# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Faik Uygur <faik@pardus.org.tr>

import unittest
import pisi.api
import pisi

class ConflictTestCase(unittest.TestCase):
    def setUp(self):
        pisi.api.init(write=False)
        
        d_t = {}
        packages = {"a": ["z", "t", "d"],
                    "b": ["a", "e", "f"],
                    "c": ["g", "h"],
                    "d": [],
                    "e": ["j"],
                    "amigo" : ["pciutils", "agimo", "libpng", "ncurses", "soniga"],
                    "imago" : ["less"],
                    "gomia" : ["hede", "hodo", "libpng"],
                    "omiga" : []}

        for name in packages.keys():
            pkg = pisi.specfile.Package()
            pkg.name = name
            pkg.conflicts = packages[name]
            d_t[name] = pkg

        class PackageDB:
            def get_package(self, key):
                return d_t[str(key)]

        self.packagedb = PackageDB()

    def tearDown(self, ):
        pisi.api.finalize()

    def testConflictWithEachOther(self):
        packages = ["a", "b", "c", "d", "e"]
        (C, D, pkg_conflicts) = pisi.operations.calculate_conflicts(packages, self.packagedb)
        self.assert_(['a', 'b', 'e', 'd'] == list(D))

    def testConflictWithInstalled(self):
        packages = ["amigo", "imago", "omiga"]
        (C, D, pkg_conflicts) = pisi.operations.calculate_conflicts(packages, self.packagedb)
        self.assert_(not D)
        self.assert_(['libpng', 'ncurses', 'less', 'pciutils'] == list(C))
        self.assert_(['libpng', 'ncurses', 'pciutils'] == list(pkg_conflicts["amigo"]))
        self.assert_("agimo" not in list(pkg_conflicts["amigo"]))

    def testConflictWithEachOtherAndInstalled(self):
        packages = ["amigo", "imago", "a", "b", "c"]
        (C, D, pkg_conflicts) = pisi.operations.calculate_conflicts(packages, self.packagedb)
        self.assert_(['a', 'b'] == list(D))
        self.assert_(['libpng', 'ncurses', 'less', 'pciutils'] == list(C))
        self.assert_(['libpng', 'ncurses', 'pciutils'] == list(pkg_conflicts["amigo"]))
        self.assert_("agimo" not in list(pkg_conflicts["amigo"]))

suite = unittest.makeSuite(ConflictTestCase)

# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import unittest
import os

from pisi.dependency import *

class DependencyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testVersionFrom(self):
        # a real life story bug #603
        gtkmmdep = Dependency()
        gtkmmdep.versionFrom = '1.9.1'
        gtkmmdep.package = 'atk'
        self.assert_( not gtkmmdep.satisfies_relation('atk', '1.8.0', '1') )
        self.assert_( gtkmmdep.satisfies_relation('atk', '1.9.1', '2') )
        self.assert_( gtkmmdep.satisfies_relation('atk', '1.10.5', '3') )

    def testReleaseFrom(self):
        # releaseFrom isn't taken into account #2294
        dep = Dependency()
        dep.releaseFrom = '121'
        dep.package = 'dbus'
        self.assert_(not dep.satisfies_relation('dbus', '1.2', '2'))

    def testReleaseTo(self):
        dep = Dependency()
        dep.releaseTo = '22'
        dep.package = 'dbus'
        self.assert_(not dep.satisfies_relation('dbus', '1.2', '25'))

    def testReleaseIs(self):
        dep = Dependency()
        dep.release = '42'
        dep.package = 'dbus'
        self.assert_(dep.satisfies_relation('dbus', '1.2', '42'))

suite = unittest.makeSuite(DependencyTestCase)

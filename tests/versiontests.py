# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import os

from pisi import version

class VersionTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testOps(self):
        v1 = version.Version("0.3.1")
        v2 = version.Version("0.3.5")
        v3 = version.Version("1.5.2-4")
        v4 = version.Version("0.3.1-1")
        self.assert_(v1 < v2)
        self.assert_(v3 > v2)
        self.assert_(v1 <= v3)
        self.assert_(v4 >= v4)

        # with keywords
        v1 = version.Version("2.23_pre10")
        v2 = version.Version("2.23")
        v3 = version.Version("2.21")
        v4 = version.Version("2.23_p1")
        v5 = version.Version("2.23_beta1")
        self.assert_(v1 < v2)
        self.assert_(v1 > v3)
        self.assert_(v1 < v4)
        self.assert_(v1 > v5)
        self.assert_(v2 < v4)
        self.assert_(v2 > v5)

        # with character
        v1 = version.Version("2.10a")
        v2 = version.Version("2.10")
        v3 = version.Version("2.10d")
        self.assert_(v1 > v2)
        self.assert_(v1 < v3)
        self.assert_(v2 < v3)

        v1 = version.Version("pisi-1.0_alpha1")
        v2 = version.Version("pisi-1.0_alpha2")
        self.assert_(v2 > v1)

suite = unittest.makeSuite(VersionTestCase)

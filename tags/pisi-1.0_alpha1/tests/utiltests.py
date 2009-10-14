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
from pisi.util import *

class UtilTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def testSubPath(self):
        self.assert_(subpath('usr', 'usr'))
        self.assert_(subpath('usr', 'usr/local/src'))
        self.assert_(not subpath('usr/local', 'usr'))

    def testRemovePathPrefix(self):
        a = removepathprefix('usr/local', 'usr/local/lib')
        self.assertEqual(a, 'lib')

        a = removepathprefix('usr/local/', 'usr/local/lib')
        self.assertEqual(a, 'lib')


suite = unittest.makeSuite(UtilTestCase)

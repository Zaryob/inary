# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author: Eray Ozkural <eray@uludag.org.tr>

import unittest
import os

from pisi.dependency import *

class DependencyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testDep(self):
        # a real life story bug #603
        gtkmmdep = DepInfo()
        gtkmmdep.versionFrom = '1.9.1'
        gtkmmdep.package = 'atk'
        self.assert_( not gtkmmdep.satisfies('atk', '1.8.0', 1) )
        
suite = unittest.makeSuite(DependencyTestCase)

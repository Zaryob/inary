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

    def test603(self):
        # a real life story bug #603
        gtkmmdep = Dependency()
        gtkmmdep.versionFrom = '1.9.1'
        gtkmmdep.package = 'atk'
        self.assert_( not gtkmmdep.satisfies('atk', '1.8.0', '1') )

    def test2294(self):
        # releaseFrom isn't taken into account
        dep = Dependency()
        dep.releaseFrom = '121'
        dep.package = 'dbus'
        self.assert_(not dep.satisfies('dbus', '1.2', '2'))
    
suite = unittest.makeSuite(DependencyTestCase)

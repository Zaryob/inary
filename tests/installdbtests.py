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

from pisi.installdb import installdb
from pisi import util
from pisi.config import config

class InstallDBTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def testRemoveDummy(self):
        installdb.remove('installtest')
        self.assert_(not installdb.is_installed('installtest'))
        
    def testInstall(self):
        installdb.purge('installtest')
        installdb.install('installtest', '0.1', '2', '3')

    def testRemovePurge(self):
        installdb.install('installtest', '0.1', '2', '3')
        self.assert_(installdb.is_installed('installtest'))
        installdb.remove('installtest')
        self.assert_(installdb.is_removed('installtest'))
        installdb.purge('installtest')
        self.assert_(not installdb.is_recorded('installtest'))

suite = unittest.makeSuite(InstallDBTestCase)

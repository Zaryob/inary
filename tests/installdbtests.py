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

import pisi.context as ctx
import pisi.api
import pisi.installdb
from pisi import util

class InstallDBTestCase(unittest.TestCase):

    def setUp(self):
        pisi.api.init()
        self.installdb = ctx.installdb

    def testRemoveDummy(self):
        self.installdb.remove('installtest')
        self.assert_(not self.installdb.is_installed('installtest'))
        
    def testInstall(self):
        self.installdb.purge('installtest')
        self.installdb.install('installtest', '0.1', '2', '3')

    def testRemovePurge(self):
        self.installdb.install('installtest', '0.1', '2', '3')
        self.assert_(self.installdb.is_installed('installtest'))
        self.installdb.remove('installtest')
        self.assert_(self.installdb.is_removed('installtest'))
        self.installdb.purge('installtest')
        self.assert_(not self.installdb.is_recorded('installtest'))

suite = unittest.makeSuite(InstallDBTestCase)

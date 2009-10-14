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
from pisi.packagedb import PackageDB
from pisi import util
from pisi.specfile import SpecFile

class PackageDBTestCase(unittest.TestCase):

    def setUp(self):
        # setUp will be called for each test individually
        pisi.api.init()

        self.spec = SpecFile()
        self.spec.read('tests/popt/pspec.xml')

        self.pdb = PackageDB('testdb')
        
    def testAdd(self):
        self.pdb.add_package(self.spec.packages[0])
        self.assert_(self.pdb.has_package('popt-libs'))
        # close the database and remove lock
        del self.pdb
    
    def testRemove(self):
        self.pdb.remove_package('popt-libs')
        self.assert_(not self.pdb.has_package('popt-libs'))
        del self.pdb

suite = unittest.makeSuite(PackageDBTestCase)


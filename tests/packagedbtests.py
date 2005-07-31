
import unittest
import os

from pisi.packagedb import PackageDB
from pisi import util
from pisi import context

class PackageDBTestCase(unittest.TestCase):

    def setUp(self):
        # setUp will be called for each test individually
        self.ctx = context.BuildContext('tests/popt/pspec.xml')
        self.pdb = PackageDB('testdb')
        
    def testAdd(self):
        self.pdb.add_package(self.ctx.spec.packages[0])
        self.assert_(self.pdb.has_package('popt-libs'))
        # close the database and remove lock
        del self.pdb
    
    def testRemove(self):
        self.pdb.remove_package('popt-libs')
        self.assert_(not self.pdb.has_package('popt-libs'))
        del self.pdb

suite = unittest.makeSuite(PackageDBTestCase)


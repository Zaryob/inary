
import unittest
import os

from pisi.packagedb import PackageDB
from pisi import util
from pisi import context

class PackageDBTestCase(unittest.TestCase):

    def setUp(self):
        self.ctx = context.BuildContext('tests/popt/pspec.xml')
        self.pdb = PackageDB('testdb')
        
    def testAdd(self):
        self.pdb.add_package(self.ctx.spec.packages[0])
        self.assert_(self.pdb.has_package('popt-libs'))
    
    def testRemove(self):
        self.pdb.remove_package('popt-libs')
        self.assert_(not self.pdb.has_package('popt-libs'))

suite = unittest.makeSuite(PackageDBTestCase)


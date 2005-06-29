
import unittest
import os

from pisi.packagedb import packagedb
from pisi import util
from pisi import context

class PackageDBTestCase(unittest.TestCase):

    def setUp(self):
        self.ctx = context.BuildContext('samples/popt/pspec.xml')
        
    def testAdd(self):
        packagedb.add_package(self.ctx.spec.packages[0])
        self.assert_(packagedb.has_package('popt-libs'))
    
    def testRemove(self):
        self.testAdd()
        packagedb.remove_package('popt-libs')
        self.assert_(not packagedb.has_package('popt-libs'))

suite = unittest.makeSuite(PackageDBTestCase)


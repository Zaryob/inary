
import unittest
import os

from pisi import packagedb
from pisi import util
from pisi import context

class PackageDBTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = context.Context("samples/popt/popt.pspec")
        
    def testAdd(self):
        packagedb.add_package("testpackagedb", self.ctx.spec.packages[0])
        self.assert_(packagedb.has_package("testpackagedb"))
    
    def testRemove(self):
        self.testAdd()
        packagedb.remove_package("testpackagedb")
        self.assert_(not packagedb.has_package("testpackagedb"))

suite = unittest.makeSuite(PackageDBTestCase)

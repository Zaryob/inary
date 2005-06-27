
import unittest
import os

from pisi import packagedb
from pisi import util
from pisi import context

class SourceDBTestCase(unittest.TestCase):

    def setUp(self):
        self.ctx = context.BuildContext("samples/popt/popt.pspec")
        
    def testAdd(self):
        sourcedb.add_source("testsourcedb", self.ctx.spec.source)
        self.assert_(sourcedb.has_package("testsourcedb"))
    
    def testRemove(self):
        self.testAdd()
        sourcedb.remove_package("testsourcedb")
        self.assert_(not sourcedb.has_package("testsourcedb"))

suite = unittest.makeSuite(SourceDBTestCase)

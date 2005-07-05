
import unittest
import os

from pisi.sourcedb import sourcedb
from pisi import util
from pisi import context

class SourceDBTestCase(unittest.TestCase):

    def setUp(self):
        self.ctx = context.BuildContext("tests/popt/pspec.xml")
        
    def testAdd(self):
        sourcedb.add_source(self.ctx.spec.source)
        self.assert_(sourcedb.has_source("popt"))
    
    def testRemove(self):
        self.testAdd()
        sourcedb.remove_source("popt")
        self.assert_(not sourcedb.has_source("popt"))

suite = unittest.makeSuite(SourceDBTestCase)

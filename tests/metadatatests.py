
import unittest
import os

from pisi import metadata
from pisi import util
from pisi import context

class MetaDataTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def testReadWrite(self):
        md = metadata.MetaData()
        md.read('tests/sandbox/metadata.xml')

suite = unittest.makeSuite(MetaDataTestCase)

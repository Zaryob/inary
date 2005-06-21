
import unittest
import os

from pisi import metadata
from pisi import util
from pisi import context

class MetaDataTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def testRead(self):
        md = metadata.MetaData()
        md.read('tests/sandbox/metadata.xml')

        self.assertEqual(md.license, "As-Is")

        self.assertEqual(md.version, "0.1")

        self.assertEqual(md.installedSize, 40500)

    def testWrite(self):
        pass

suite = unittest.makeSuite(MetaDataTestCase)

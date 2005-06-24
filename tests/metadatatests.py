
import unittest
import os

from pisi import metadata
from pisi import util
from pisi.config import config

class MetaDataTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def testRead(self):
        md = metadata.MetaData()
        md.read('tests/sandbox/metadata.xml')

        self.assertEqual(md.package.license, "As-Is")

        self.assertEqual(md.package.version, "1.7")

        self.assertEqual(md.package.installedSize, 546542)
        return md
    
    def testWrite(self):
        md = self.testRead()
        md.write(os.path.join(config.tmp_dir(),'metadata-test.xml' ))
        

suite = unittest.makeSuite(MetaDataTestCase)

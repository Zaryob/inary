import unittest
import os

from inary.data import metadata
from inary import util

class MetadataTestCase(unittest.TestCase):

    def testRead(self):
        md = metadata.MetaData()
        md.read("../addfiles/metadata.xml")
        self.assertEqual(md.package.license,["As-Is"])
        self.assertEqual(md.package.version,"1.7")
        self.assertEqual(md.package.installedSize,149691)
        return md

    def testVerify(self):
        md = self.testRead()
        if md.errors():
            self.fail()

    def testWrite(self):
        md = self.testRead()
        md.write("/tmp/metadata-write.xml")




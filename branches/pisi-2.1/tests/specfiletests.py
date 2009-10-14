import unittest
import os
import pisi.specfile as specfile
import pisi.util as util

class SpecFileTestCase(unittest.TestCase):
    def setUp(self):
        self.spec = specfile.SpecFile()
        self.spec.read('repos/pardus-2007/system/base/curl/pspec.xml')

    def testGetSourceVersion(self):
        assert '0.3' == self.spec.getSourceVersion()

    def testGetSourceRelease(self):
        assert '1' == self.spec.getSourceRelease()

    def testVerify(self):
        if self.spec.errors():
            self.fail()

    def testCopy(self):
        self.spec.read('repos/pardus-2007/system/base/curl/pspec.xml')
        self.spec.write('repos/pardus-2007/system/base/curl/pspec.xml')














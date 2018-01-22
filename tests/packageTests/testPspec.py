import unittest
import os
import inary.data.specfile as specfile
import inary.util as util

class SpecFileTestCase(unittest.TestCase):
    def setUp(self):
        self.spec = specfile.SpecFile()
        self.spec.read('../repos/repo1/system/base/ncurses/pspec.xml')

    def testGetSourceVersion(self):
        assert '6.0' == self.spec.getSourceVersion()

    def testGetSourceRelease(self):
        assert '1' == self.spec.getSourceRelease()

    def testVerify(self):
        if self.spec.errors():
            self.fail()

    def testCopy(self):
        self.spec.read('../repos/repo1/system/base/ncurses/pspec.xml')
        self.spec.write('../repos/repo1/system/base/ncurses/pspec.xml')














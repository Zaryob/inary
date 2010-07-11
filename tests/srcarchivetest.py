import unittest
import pisi.sourcearchive
from pisi.specfile import SpecFile

class SourceArchiveTestCase(unittest.TestCase):

    def testFetch(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        srcarch = pisi.sourcearchive.SourceArchive(spec.source.archive[0], targetDir)
        self.assert_(not srcarch.fetch())

    def testIscached(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        srcarch = pisi.sourcearchive.SourceArchive(spec.source.archive[0], targetDir)
        assert srcarch.is_cached()

    def testIscached(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        srcarch = pisi.sourcearchive.SourceArchive(spec.source.archive[0], targetDir)
        self.assert_(not srcarch.unpack())

    def testUnpack(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        srcarch = pisi.sourcearchive.SourceArchive(spec.source.archive[0], targetDir)
        srcarch.unpack()

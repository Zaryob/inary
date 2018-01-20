import unittest
import inary.sourcearchive
from inary.data.specfile import SpecFile

class SourceArchiveTestCase(unittest.TestCase):

    def testFetch(self):
        spec = SpecFile('repos/repo1/system/base/curl/pspec.xml')
        srcarch = inary.sourcearchive.SourceArchive(spec.source.archive[0])
        self.assertTrue(not srcarch.fetch())

    def testIscached(self):
        spec = SpecFile('repos/repo1/system/base/curl/pspec.xml')
        srcarch = inary.sourcearchive.SourceArchive(spec.source.archive[0])
        assert srcarch.is_cached()

    def testIscached(self):
        spec = SpecFile('repos/repo1/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        srcarch = inary.sourcearchive.SourceArchive(spec.source.archive[0])
        self.assertTrue(not srcarch.unpack(targetDir))

    def testUnpack(self):
        spec = SpecFile('repos/repo1/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        srcarch = inary.sourcearchive.SourceArchive(spec.source.archive[0])
        srcarch.unpack(targetDir)

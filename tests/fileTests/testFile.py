import unittest
from inary.data.specfile import SpecFile
from inary import uri
from inary.file import File

class FileTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testMakeUri(self):
        spec = SpecFile("repos/repo1/system/base/bash/pspec.xml")
        url = uri.URI(spec.source.archive[0].uri)
        self.assertTrue(File.make_uri(url))

    def testChooseMethod(self):
        compress = File('repos/repo2/inary-index.xml', File.read)
        self.assertTrue(File.choose_method('inary.conf', compress))

    def testDecompress(self):
        localfile = File('repos/repo1/system/base/bash/pspec.xml', File.read)
        compress = File('repos/repo2/inary-index.xml', File.read)
        self.assertTrue(File.decompress(localfile,compress))

    def testLocalFile(self):
        f = File('repos/repo1/system/base/curl/pspec.xml', File.read)
        r = f.readlines()
        assert (len(r) > 0)

    def testRemoteRead(self):
        f = File('http://www.sulin.org.tr/Releases/2018/roadmap.html', File.read)
        r = f.readlines()
        assert (len(r) > 0)

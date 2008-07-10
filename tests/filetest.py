import unittest
from pisi.specfile import SpecFile
from pisi import uri
from pisi.file import File

class FileTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testMakeUri(self):
        self.spec = SpecFile()
        self.url = uri.URI(self.spec.source.archive.uri)
        f = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        self.assert_(f.make_uri('uri'))

    def testChooseMethod(self):
        compress = File('repos/contrib-2007/pisi-index.xml.bz2', File.read)
        self.assert_(File.choose_method('pisi.conf', compress))

    def testDecompress(self):
        localfile = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        compress = File('repos/contrib-2007/pisi-index.xml.bz2', File.read)
        self.assert_(File.decompress(localfile,compress))

    def testLocalFile(self):
        f = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        r = f.readlines()
        assert (len(r) > 0)

    def testIsatty(self):
        f = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        assert not f.isatty()

    def testFileNo(self):
        f = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        assert 3 == f.fileno()

    def testRemoteRead(self):
        f = File('http://uludag.org.tr/bulten/index.html', File.read)
        r = f.readlines()
        assert (len(r) > 0)



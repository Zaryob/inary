import unittest
from inary.specfile import SpecFile
from inary import uri
from inary.file import File

class FileTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testMakeUri(self):
        spec = SpecFile("repos/pardus-2007/system/base/curl/pspec.xml")
        url = uri.URI(spec.source.archive[0].uri)
        self.assertTrue(File.make_uri(url))

    def testChooseMethod(self):
        compress = File('repos/contrib-2007/inary-index.xml', File.read)
        self.assertTrue(File.choose_method('inary.conf', compress))

    def testDecompress(self):
        localfile = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        compress = File('repos/contrib-2007/inary-index.xml', File.read)
        self.assertTrue(File.decompress(localfile,compress))

    def testLocalFile(self):
        f = File('repos/pardus-2007/system/base/curl/pspec.xml', File.read)
        r = f.readlines()
        assert (len(r) > 0)

    def testRemoteRead(self):
        f = File('http://www.pardus.org.tr/urunler/pardus-2009.2-Geronticus_eremita-surum-notlari-tr.html', File.read)
        r = f.readlines()
        assert (len(r) > 0)



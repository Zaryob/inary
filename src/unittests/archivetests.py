
import unittest
from os.path import exists as pathexists
from os.path import basename

from pisi import archive
from pisi import specfile
from pisi import fetcher
from pisi import util

class ArchiveFileTestCase(unittest.TestCase):
    def setUp(self):
	self.spec = specfile.SpecFile()
        self.spec.read("samples/popt.pspec")
	
    def testUnpackTar(self):
	achv = archive.Archive(self.spec.source.archiveType,
			       self.spec.source.archiveName)
	
	assert self.spec.source.archiveType == "targz"

	# unpacking is trivial with Archive()
	achv.unpack()
	
	# but testing is hard
	assert pathexists("popt-1.7")

	testfile = "popt-1.7/Makefile.am"
	assert pathexists(testfile)
	
	self.assertEqual(util.md5_file(testfile),
			 "171545adab7b51ebf6ec5575d3000a95")

    def testUnpackZip(self):
	# first, we need to fetch a zip file
	uri = "http://cekirdek.uludag.org.tr/~meren/sandbox.zip"
	filename = basename(uri)
	fetch = fetcher.Fetcher(uri, filename)
	fetch.fetch()

	achv = archive.Archive("zip", filename)
	achv.unpack()
	

suite = unittest.makeSuite(ArchiveFileTestCase)
	    

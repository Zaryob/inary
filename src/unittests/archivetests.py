
import unittest
from os.path import exists as pathexists

from pisi import archive
from pisi import specfile
from pisi import util

class ArchiveFileTestCase(unittest.TestCase):
    def setUp(self):
	self.spec = specfile.SpecFile()
        self.spec.read("samples/popt.pspec")
	
	self.achv = archive.Archive(self.spec.source.archiveType,
				    self.spec.source.archiveName)

    def testUnpackTar(self):
	assert self.spec.source.archiveType == "targz"

	# unpacking is trivial with Archive()
	self.achv.unpack()
	
	# but testing is hard
	assert pathexists("popt-1.7")

	testfile = "popt-1.7/Makefile.am"
	assert pathexists(testfile)
	
	self.assertEqual(util.md5_file(testfile),
			 "171545adab7b51ebf6ec5575d3000a95")

suite = unittest.makeSuite(ArchiveFileTestCase)
	    

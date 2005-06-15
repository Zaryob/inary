
import unittest
from os.path import exists as pathexists
from os.path import basename, islink

from pisi import archive
from pisi import specfile
from pisi import fetcher
from pisi import util
from pisi import config

class ArchiveFileTestCase(unittest.TestCase):
    def setUp(self):
	self.spec = specfile.SpecFile()
        self.spec.read("samples/popt.pspec")
	
    def testUnpackTar(self):
	targetDir = config.build_work_dir(self.spec.source.name,
					  self.spec.source.version,
					  self.spec.source.release)
	achv = archive.Archive(self.spec.source.archiveType,
			       self.spec.source.archiveName,
			       targetDir)
	
	assert self.spec.source.archiveType == "targz"

	# unpacking is trivial with Archive()
	achv.unpack()
	
	# but testing is hard
	# "var/tmp/pisi/popt-1.7-3/work" (targetDir)
	assert pathexists(targetDir + "/popt-1.7")

	testfile = targetDir + "/popt-1.7/Makefile.am"
	assert pathexists(testfile)
	
	# check file integrity
	self.assertEqual(util.md5_file(testfile),
			 "171545adab7b51ebf6ec5575d3000a95")

    def testUnpackZip(self):
	# first, we need to fetch a zip file
	uri = "http://cekirdek.uludag.org.tr/~meren/sandbox.zip"
	filename = basename(uri)
	fetch = fetcher.Fetcher(uri, filename)
	fetch.fetch()

	# imaginary name, version and release for our test zip file
	targetDir = config.build_work_dir("sandbox", "0.1", "1")

	achv = archive.Archive("zip", filename, targetDir)
	achv.unpack()

	assert pathexists(targetDir + "/sandbox")

	testfile = targetDir + "/sandbox/borek.cs"
	assert pathexists(testfile)
	
	# check file integrity
	self.assertEqual(util.md5_file(testfile),
			 "1e0c3f1e4664ee8ca67caea8b6b12ea4")

	# check for symbolic links
	testfile = targetDir + "/sandbox/deneme/hed"
	assert islink(testfile)
	


suite = unittest.makeSuite(ArchiveFileTestCase)

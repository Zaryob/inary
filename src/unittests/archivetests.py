
import unittest
from os.path import exists as pathexists
from os.path import basename, islink

from pisi import archive
from pisi import fetcher
from pisi import util
from pisi import context

class ArchiveFileTestCase(unittest.TestCase):
#     def setUp(self):
# 	pass

    def testUnpackTar(self):
	ctx = context.Context("samples/popt/popt.pspec")

	targetDir = ctx.build_work_dir()
	achv = archive.Archive(ctx)
	
	assert ctx.spec.source.archiveType == "targz"

	# unpacking is trivial with Archive()
	achv.unpack(targetDir)
	
	# but testing is hard
	# "var/tmp/pisi/popt-1.7-3/work" (targetDir)
	assert pathexists(targetDir + "/popt-1.7")

	testfile = targetDir + "/popt-1.7/Makefile.am"
	assert pathexists(testfile)
	
	# check file integrity
	self.assertEqual(util.md5_file(testfile),
			 "171545adab7b51ebf6ec5575d3000a95")

    def testUnpackZip(self):
	ctx = context.Context("unittests/sandbox/sandbox.pspec")
	fetch = fetcher.Fetcher(ctx)
	fetch.fetch()

	targetDir = ctx.build_work_dir()

	assert ctx.spec.source.archiveType == "zip"

	achv = archive.Archive(ctx)
	achv.unpack(targetDir)

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

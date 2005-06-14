
import unittest
import os

from pisi import fetcher
from pisi import specfile
from pisi import util

class FetcherTestCase(unittest.TestCase):
    def setUp(self):
	self.spec = specfile.SpecFile()
	self.spec.read("samples/popt.pspec")

	self.fetch = fetcher.Fetcher(self.spec.source.archiveUri,
				     self.spec.source.archiveName)
	
    def testFetch(self):
	self.fetch.fetch()
	destpath = self.fetch.filedest + "/" + self.fetch.filename
	if os.access(destpath, os.R_OK):
            self.assertEqual(util.md5_file(destpath),
			     self.spec.source.archiveMD5)


suite = unittest.makeSuite(FetcherTestCase)

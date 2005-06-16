
import unittest
import os

from pisi import fetcher
from pisi import util
from pisi import context

class FetcherTestCase(unittest.TestCase):
    def setUp(self):
	self.ctx = context.Context("samples/popt/popt.pspec")

	self.fetch = fetcher.Fetcher(self.ctx)
	
    def testFetch(self):
	self.fetch.fetch()
	destpath = self.fetch.filedest + "/" + self.fetch.filename
	if os.access(destpath, os.R_OK):
            self.assertEqual(util.md5_file(destpath),
			     self.ctx.spec.source.archiveMD5)


suite = unittest.makeSuite(FetcherTestCase)

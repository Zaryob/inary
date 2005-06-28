
import unittest
import os

from pisi import fetcher
from pisi import util
from pisi import context
from pisi import config
from pisi import purl

class FetcherTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = context.BuildContext("samples/popt/popt.pspec")
        self.url = purl.PUrl(self.ctx.spec.source.archiveUri)
        self.destpath = config.config.archives_dir()
        self.fetch = fetcher.Fetcher(self.url, self.destpath)
    
    def testFetch(self):
        self.fetch.fetch()
        fetchedFile = os.path.join(self.destpath, self.url.filename())
        if os.access(fetchedFile, os.R_OK):
            self.assertEqual(util.sha1_file(fetchedFile),
                 self.ctx.spec.source.archiveSHA1)

suite = unittest.makeSuite(FetcherTestCase)

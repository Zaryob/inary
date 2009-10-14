import unittest
import os
import base64
import pisi.context as ctx
import pisi.api
from pisi.specfile import SpecFile
from pisi.fetcher import Fetcher
from pisi import util
from pisi import uri

class FetchTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.spec = SpecFile()
        self.spec.read('repos/pardus-2007/system/base/curl/pspec.xml')
        self.url = uri.URI(self.spec.source.archive.uri)
        self.url.set_auth_info(("user", "pass"))
        self.destpath = ctx.config.archives_dir()
        self.fetch = Fetcher(self.url, self.destpath)

    def testFetch(self):
        self.fetch.fetch()
        fetchedFile = os.path.join(self.destpath, self.url.filename())
        if os.access(fetchedFile, os.R_OK):
            self.assertEqual(util.sha1_file(fetchedFile),self.spec.source.archive.sha1sum)
        os.remove(fetchedFile)

    def testFetcherFunctions(self):
        enc = base64.encodestring('%s:%s' % self.url.auth_info())
        self.assertEqual(self.fetch._get_http_headers(),(('Authorization', 'Basic %s' % enc),))
        assert not self.fetch._get_ftp_headers()




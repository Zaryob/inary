
# -*- coding: utf-8 -*-

# Yet another Pisi module for fetching files from various sources. Of
# course, this is not limited to just fetching source files. We fetch
# all kinds of things: source tarballs, index files, packages, and God
# knows what.

# python standard library modules
import urllib2
import os
from urllib import addinfourl
from base64 import encodestring

# pisi modules
import util
from purl import PUrl
from ui import ui

class FetchError (Exception):
    pass

# helper functions
def fetchUrl(url, dest, progress=None):
    fetch = Fetcher(url, dest)
    fetch.progress = progress
    fetch.fetch()
    if progress:
        ui.info('\n')


class Fetcher:
    """Fetcher can fetch a file from various sources using various
    protocols."""
    def __init__(self, url, dest):
        if not isinstance(url, PUrl):
            url = PUrl(url)
 
        self.url = url
        self.filedest = dest
        util.check_dir(self.filedest)
        self.percent = 0
        self.rate = 0.0
        self.progress = None
        self.existSize = 0

    def fetch (self):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            self.err("filename error")

        if not os.access(self.filedest, os.W_OK):
            self.err("no perm to write to dest dir")

        if self.url.isLocalFile():
            self.fetchLocalFile()
        else:
            self.fetchRemoteFile()

        return os.path.join(self.filedest, self.url.filename())

    def doGrab(self, fileURI, dest, totalsize):
        symbols = [' B/s', 'KB/s', 'MB/s', 'GB/s']
        from time import time
        tt, oldsize = int(time()), 0
        bs, size = 1024, 0
        symbol, depth = "B/s", 0
        st = time()
        chunk = fileURI.read(bs)
        size = size + len(chunk)
        if self.progress:
            p = self.progress(totalsize)
            self.percent = p.update(size)
        while chunk:
            dest.write(chunk)
            chunk = fileURI.read(bs)
            size = size + len(chunk)
            ct = time()
            if int(tt) != int(ct):
                self.rate = size / (ct - st)
                while self.rate > 1000 and depth < 3:
                    self.rate /= 1024
                    depth += 1
                symbol, depth = symbols[depth], 0
                oldsize, tt = size, time()
            if self.progress:
                if p.update(size):
                    self.percent = p.percent
                    retval = {'filename': self.url.filename(), 
                              'percent' : self.percent,
                              'rate': self.rate,
                              'symbol': symbol}
                    ui.displayProgress(retval)

        dest.close()

    def fetchLocalFile (self):
        url = self.url

        if not os.access(url.path(), os.F_OK):
            self.err("no such file or no perm to read")

        dest = open(os.path.join(self.filedest, url.filename()) , "wb")
        totalsize = os.path.getsize(url.path())
        fileObj = open(url.path())
        self.doGrab(fileObj, dest, totalsize)

    def fetchRemoteFile (self):
        from httplib import HTTPException

        localFile = os.path.join(self.filedest, self.url.filename())

        if os.path.exists(localFile) and self.url.scheme() == "http" or self.url.scheme() == "https":
            self.existSize = os.path.getsize(localFile)
            ui.info('Resuming (%d bytes already downloaded)...\n' % self.existSize)
            dest = open(localFile, "ab")
        else:
            dest = open(localFile, "wb")
                
        try:
            fileObj = urllib2.urlopen(self.formatRequest(urllib2.Request(self.url.uri)))
            headers = fileObj.info()
    
        except ValueError, e:
            self.err('%s' % (e, ))
        except IOError, e:
            self.err('%s' % (e, ))
        except OSError, e:
            self.err('%s' % (e, ))
        except HTTPException, e:
            self.err(('(%s): %s') % (e.__class__.__name__, e))

        if headers and not headers.has_key('Content-Length'):
            totalsize = 0 # could not get the totalsize of file
        else: totalsize = int(headers['Content-Length'])

        self.doGrab(fileObj, dest, totalsize)

    def formatRequest(self, request):
        authinfo = self.url.authInfo()
        if authinfo:
            enc = encodestring("%s:%s" % authinfo)
            request.add_header('Authorization', 'Basic %s' % enc)
        if self.existSize:
            range_handler = HTTPRangeHandler()
            opener = urllib2.build_opener(range_handler)
            urllib2.install_opener(opener)
            request.add_header('Range', 'bytes=%d-' % self.existSize)
        return request

    def err (self, error):
        raise FetchError(error)

class HTTPRangeHandler(urllib2.BaseHandler):
    """ 
    "urllib2, the 'Error 206: Partial Content'
    reponse from the HTTP server is really what we expected.
    Don't give up, resume the download..
    """

    def http_error_206(self, request, fp, errcode, msg, headers):
        return addinfourl(fp, headers, request.get_full_url())

    def http_error_416(self, request, fp, errcode, msg, headers):
        # HTTP 1.1's 'Range Not Satisfiable' error..
        raise FetchError('Requested Range Not Satisfiable')

class FTPRangeHandler:
    pass

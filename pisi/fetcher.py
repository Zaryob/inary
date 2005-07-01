# -*- coding: utf-8 -*-

# Yet another Pisi module for fetching files from various sources. Of
# course, this is not limited to just fetching source files. We fetch
# all kinds of things: source tarballs, index files, packages, and God
# knows what.

# python standard library modules
import urllib2
import os

# pisi modules
import util
from purl import PUrl
from ui import ui

class FetchError (Exception):
    pass

# helper functions
def displayProgress(pd):
    out = '\r%-30.30s %3d%% %12.2f %s' % \
        (pd['filename'], pd['percent'], pd['rate'], pd['symbol'])
    ui.info(out)

def fetchUrl(url, dest, percentHook=None):
    fetch = Fetcher(url, dest)
    fetch.percentHook = percentHook
    fetch.fetch()
    if percentHook:
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
        self.percentHook = None

    def fetch (self):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            self.err("filename error")

        if os.access(self.filedest, os.W_OK) == False:
            self.err("no perm to write to dest dir")

        scheme_err = lambda: self.err("unexpected scheme")

        if self.url.isLocalFile():
            self.fetchLocalFile()
        else:
            self.fetchRemoteFile()

        return os.path.join(self.filedest, self.url.filename())

    def doGrab(self, fileURI, dest, totalsize):
        symbols = [' B/s', 'KB/s', 'MB/s', 'GB/s']
        from time import time
        tt, oldsize = int(time()), 0
        p = Progress(totalsize)
        bs, size = 1024, 0
        symbol, depth = "B/s", 0
        st = time()
        chunk = fileURI.read(bs)
        size = size + len(chunk)
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
            if p.update(size):
                self.percent = p.percent
                if self.percentHook != None:
                    retval = {'filename': self.url.filename(), 
                              'percent' : self.percent,
                              'rate': self.rate,
                              'symbol': symbol}
                    self.percentHook(retval)

        dest.close()

    def fetchLocalFile (self):
        url = self.url

        if os.access(url.path(), os.F_OK) == False:
            self.err("no such file or no perm to read")

        dest = open(os.path.join(self.filedest, url.filename()) , "w")
        totalsize = os.path.getsize(url.path())
        fileURI = open(url.path())
        self.doGrab(fileURI, dest, totalsize)

    def fetchRemoteFile (self):
        from httplib import HTTPException

        try:
            fileURI = urllib2.urlopen(self.url.uri)
            headers = fileURI.info()
    
        except ValueError, e:
            self.err('%s' % (e, ))
        except IOError, e:
            self.err('%s' % (e, ))
        except OSError, e:
            self.err('%s' % (e, ))
        except HTTPException, e:
            self.err(('(%s): %s') % (e.__class__.__name__, e))

        if not headers is None and not headers.has_key('Content-Length'):
            totalsize = 0 # could not get the totalsize of file
        else: totalsize = int(headers['Content-Length'])

        dest = open(os.path.join(self.filedest, self.url.filename()) , "w")
        self.doGrab(fileURI, dest, totalsize)


    def err (self, error):
        raise FetchError(error)

class Progress:
    def __init__(self, totalsize):
        self.totalsize = totalsize
        self.percent = 0

    def update(self, size):
        if not self.totalsize:
            return 100

        percent = (size * 100) / self.totalsize
        if percent and self.percent is not percent:
            self.percent = percent
            return percent
        else:
            return 0

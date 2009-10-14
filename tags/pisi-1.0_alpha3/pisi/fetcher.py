# -*- coding: utf-8 -*-

# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Yet another Pisi module for fetching files from various sources. Of
# course, this is not limited to just fetching source files. We fetch
# all kinds of things: source tarballs, index files, packages, and God
# knows what.

# python standard library modules
import urllib2
import os
from base64 import encodestring

# pisi modules
import pisi
import pisi.util as util
import pisi.context as ctx
from pisi.uri import URI


class FetchError(pisi.Error):
    pass


# helper functions
def fetch_url(url, dest, progress=None):
    fetch = Fetcher(url, dest)
    fetch.progress = progress
    fetch.fetch()
    if progress:
        pass
        #ctx.ui.info('\n')


class Fetcher:
    """Fetcher can fetch a file from various sources using various
    protocols."""
    def __init__(self, url, dest):
        if not isinstance(url, URI):
            url = URI(url)
 
        self.url = url
        self.filedest = dest
        util.check_dir(self.filedest)
        self.percent = 0
        self.rate = 0.0
        self.progress = None

    def fetch (self):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            self.err("filename error")

        if not os.access(self.filedest, os.W_OK):
            self.err("no perm to write to dest dir")

        if self.url.is_local_file():
            self.fetchLocalFile()
        else:
            self.fetchRemoteFile()

        return os.path.join(self.filedest, self.url.filename())

    def _do_grab(self, fileURI, dest, totalsize):
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
                    ctx.ui.display_progress(retval)

        dest.close()

    def fetchLocalFile (self):
        url = self.url

        if not os.access(url.path(), os.F_OK):
            self.err("no such file or no perm to read")

        dest = open(os.path.join(self.filedest, url.filename()) , "w")
        totalsize = os.path.getsize(url.path())
        fileObj = open(url.path())
        self._do_grab(fileObj, dest, totalsize)

    def fetchRemoteFile (self):
        from httplib import HTTPException

        try:
            fileObj = urllib2.urlopen(self.formatRequest\
                                     (urllib2.Request(self.url.uri)))
            headers = fileObj.info()
    
        except ValueError, e:
            self.err('%s' % (e, ))
        except IOError, e:
            self.err('%s' % (e, ))
        except OSError, e:
            self.err('%s' % (e, ))
        except HTTPException, e:
            self.err(('(%s): %s') % (e.__class__.__name__, e))

        try:
            totalsize = int(headers['Content-Length'])
        except:
            totalsize = 0

        dest = open(os.path.join(self.filedest, self.url.filename()) , "w")
        self._do_grab(fileObj, dest, totalsize)

    def formatRequest(self, request):
        authinfo = self.url.auth_info()
        if authinfo:
            enc = encodestring("%s:%s" % authinfo)
            request.add_header('Authorization', 'Basic %s' % enc)
        return request

    def err (self, error):
        raise FetchError(error)


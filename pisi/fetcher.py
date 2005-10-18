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

"""Yet another Pisi module for fetching files from various sources. Of
course, this is not limited to just fetching source files. We fetch
all kinds of things: source tarballs, index files, packages, and God
knows what."""

# python standard library modules
import urllib2
import os
from base64 import encodestring
from urllib import addinfourl
from shutil import move

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# pisi modules
import pisi
import pisi.util as util
import pisi.context as ctx
from pisi.uri import URI


class Error(pisi.Error):
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
 
        self.scheme = url.scheme()
        self.url = url
        self.filedest = dest
        util.check_dir(self.filedest)
        self.percent = 0
        self.rate = 0.0
        self.progress = None
        self.existsize = 0

    def fetch (self):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            self.err(_("Filename error"))

        if not os.access(self.filedest, os.W_OK):
            self.err(_("Access denied to write to dest dir"))

        archivefile = os.path.join(self.filedest, self.url.filename())

        if self.url.is_local_file():
            self.fetchLocalFile(archivefile + ".part")
        else:
            self.fetchRemoteFile(archivefile + ".part")

        move(archivefile + ".part", archivefile)
        return archivefile 

    def _do_grab(self, fileURI, dest, totalsize):
        symbols = [' B/s', 'KB/s', 'MB/s', 'GB/s']
        from time import time
        tt, oldsize = int(time()), 0
        bs, size = 1024, self.existsize
        symbol, depth = "B/s", 0
        st = time()
        chunk = fileURI.read(bs)
        size = size + len(chunk)
        if self.progress:
            p = self.progress(totalsize, self.existsize)
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

    def fetchLocalFile (self, archivefile):
        url = self.url

        if not os.access(url.path(), os.F_OK):
            self.err(_("No such file or no permission to read"))

        dest = open(archivefile, "w")
        totalsize = os.path.getsize(url.path())
        fileObj = open(url.path())
        self._do_grab(fileObj, dest, totalsize)

    def fetchRemoteFile (self, archivefile):
        from httplib import HTTPException

        if os.path.exists(archivefile):
            if self.scheme == "http" or self.scheme == "https":
                self.existsize = os.path.getsize(archivefile)
                dest = open(archivefile, "ab")
        else:
            dest = open(archivefile, "wb")
 
        uri = self.url.uri

        try:
            fileObj = urllib2.urlopen(self.formatRequest(urllib2.Request(uri)))
            headers = fileObj.info()
        except ValueError, e:
            self.err(_('Cannot fetch %s; value error: %s') % (uri, e))
        except IOError, e:
            self.err(_('Cannot fetch %s; %s') % (uri, e))
        except OSError, e:
            self.err(_('Cannot fetch %s; %s') % (uri, e))
        except HTTPException, e:
            self.err(_('Cannot fetch %s; (%s): %s') % (uri, e.__class__.__name__, e))

        try:
            totalsize = int(headers['Content-Length']) + self.existsize
        except:
            totalsize = 0

        self._do_grab(fileObj, dest, totalsize)

    def formatRequest(self, request):
        authinfo = self.url.auth_info()
        if authinfo:
            enc = encodestring("%s:%s" % authinfo)
            request.add_header('Authorization', 'Basic %s' % enc)
        if self.existsize and self.scheme == "http" or self.scheme == "https":
            range_handler = HTTPRangeHandler()
            opener = urllib2.build_opener(range_handler)
            urllib2.install_opener(opener)
            request.add_header('Range', 'bytes=%d-' % self.existsize)
        return request

    def err (self, error):
        raise Error(error)

class HTTPRangeHandler(urllib2.BaseHandler):
    """ 
    "to override the urllib2 error: 'Error 206: Partial Content'
    this reponse from the HTTP server is already what we expected to get.
    Don't give up, resume downloading..
    """

    def http_error_206(self, request, fp, errcode, msg, headers):
        return addinfourl(fp, headers, request.get_full_url())

    def http_error_416(self, request, fp, errcode, msg, headers):
        # HTTP 1.1's 'Range Not Satisfiable' error..
        raise FetchError(_('Requested range not satisfiable'))

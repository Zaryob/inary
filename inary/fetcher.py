#-*- coding: utf-8 -*-

# Copyright (C) 2016 - 2018, Suleyman POYRAZ (AquilaNipalensis)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# python standard library modules
import os
import time
import base64
import shutil
import socket
import sys

from base64 import encodestring
from shutil import move

# Network libraries
from http.client import HTTPException
import ftplib
import urllib.request, urllib.parse, urllib.error 

#Gettext translation library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# inary modules
import inary
import inary.util as util
import inary.context as ctx
import inary.uri

# For raising errors when fetching
class FetchError(inary.Error):
    pass

# For raising errors when connecting to server
class RangeError(inary.Error):
    pass

# For raising errors when opening files
class FileError(inary.Error):
    pass

# For raising errors when connecting to server
class RemoteError(inary.Error):
    pass

class UIHandler:
    def __init__(self):
        self.filename        = None
        self.url             = None
        self.basename        = None
        self.downloaded_size = 0
        self.percent         = None
        self.rate            = 0.0
        self.size            = 0
        self.eta             = '--:--:--'
        self.symbol          = '--/-'
        self.last_updated    = 0
        self.exist_size      = 0

    def start(self, archive, url, basename, size):
        if os.path.exists(archive):
            self.exist_size = os.path.getsize(archive)
        #self.filename   = util.remove_suffix(ctx.const.partial_suffix, basename)
        self.url        = url
        self.basename   = basename
        self.total_size = size or 0

        self.now    = lambda: time.time()
        self.t_diff = lambda: self.now() - self.s_time

        self.s_time = self.now()

    def update(self, size):
        if self.size == size:
            return

        self.size = size
        if self.total_size:
            self.percent = (size * 100.0) / self.total_size
        else:
            self.percent = 0

        if int(self.now()) != int(self.last_updated) and size > 0:
            try:
                self.rate, self.symbol = util.human_readable_rate((size - self.exist_size) / (self.now() - self.s_time))
            except ZeroDivisionError:
                return
            if self.total_size:
                self.eta  = '%02d:%02d:%02d' %\
                    tuple([i for i in time.gmtime((self.t_diff() * (100 - self.percent)) / self.percent)[3:6]])

        self._update_ui()

    def end(self, read):
        pass

    def _update_ui(self):
        ctx.ui.display_progress(operation       = "fetching",
                                percent         = self.percent,
                                filename        = self.basename,
                                total_size      = self.total_size or self.size,
                                downloaded_size = self.size,
                                rate            = self.rate,
                                eta             = self.eta,
                                symbol          = self.symbol)

        self.last_updated = self.now()

class Fetcher:
    """Fetcher can fetch a file from various sources using various
    protocols."""
    def __init__(self, url, destdir="/tmp", destfile=None):
        if not isinstance(url, inary.uri.URI):
            url = inary.uri.URI(url)

        if ctx.config.get_option("authinfo"):
            url.set_auth_info(ctx.config.get_option("authinfo"))

        self.url = url
        self.destdir = destdir
        self.destfile = destfile
        self.progress = None

        self.archive_file = os.path.join(destdir, destfile or url.filename())
        self.partial_file = os.path.join(self.destdir, self.url.filename()) + ctx.const.partial_suffix

        util.ensure_dirs(self.destdir)
        self.headers_dict = {'user-agent' : 'Inary Fetcher/' + inary.__version__
                             #'http-headers' : self._get_http_headers()
                             #'ftp-headers' : self._get_ftp_headers()
                             }


    def test(self, timeout=3):
        try:
            urllib.urlopen(self.url.get_uri(),
                           proxies=self._get_proxies(),
                           timeout=timeout,
                           headers=self.headers_dict
                           )

        except ValueError as e:
            msg = _("Url Problem: \n %s") % e
            raise FetchError(msg)
            return False

        except urlerror.HTTPError as e:
            msg = _("Reaised an HTTP Error: \n %s") % e
            raise FetchError(msg)
            return False

        except Error as e:
            msg = _("Can not avaible remote server: \n %s") % e
            raise FetchError(msg)
            return False

        return True

    def fetch(self):
        """Return value: Fetched file's full path.."""
        if not self.url.filename():
            raise FileError(_('Filename error'))

        if not os.access(self.destdir, os.W_OK):
            raise FileError(_('Access denied to write to destination directory: "%s"') % (self.destdir))

        if os.path.exists(self.archive_file) and not os.access(self.archive_file, os.W_OK):
            raise FileError(_('Access denied to destination file: "%s"') % (self.archive_file))

        else:
            self.exist_size = 0

        uri = self.url.get_uri()
        try:
            try:
                try:
                    responseObj = urllib.request.urlopen(self.formatRequest(urllib.request.Request(uri)))

                except RangeError:
                    ctx.ui.info(_('Requested range not satisfiable, starting again.'))
                    self.exist_size = 0
                    responseObj = urllib.request.urlopen(self.formatRequest(urllib.request.Request(uri)))

                headers = responseObj.info()
                handler= UIHandler()

            except ValueError as e:
                raise FetchError(_('Could not fetch destination file: "%s" \nRaised Value error: "%s"') % (uri, e))
            except OSError as e:
                raise FetchError(_('Could not fetch destination file: "%s"; \n"%s"') % (uri, e))
            except urllib.error.HTTPError as e:
                raise FetchError(_('Could not fetch destination file: "%s"; \n"%s"') % (uri, e))
            except urllib.error.URLError as e:
                raise FetchError(_('Could not fetch destination file: "%s"; \n"%s"') % (uri, e[-1][-1]))
            except HTTPException as e:
                raise FetchError(_('Could not fetch destination file: "%s"; ("%s"): "%s"') % (uri, e.__class__.__name__, e))

        except FetchError as e:
            raise FetchError(_('A problem occurred. Please check the archive address and/or permissions again. %s') %e)

        total_length = int(headers['Content-Length'])

        bs=1024 #for 1MB
        chunk = responseObj.read(bs)
        downloaded_size = 0

        with open(self.partial_file, 'wb') as dest:
            if total_length:
                handler.start(self.archive_file, self.url.get_uri(), self.url.filename(), total_length)
                while chunk:
                    chunk = responseObj.read(bs)
                    dest.write(chunk)
                    downloaded_size += len(chunk)
                    handler.update(downloaded_size)
                handler.end(downloaded_size)
            else:
                ctx.ui.warning("Content-length header is missing for the fetch file, Download progress reporting will not be available")
                size=dest.tell()
                handler.start(self.archive_file, self.url.get_uri(), self.url.filename(), size)
                while chunk:
                    chunk = responseObj.read(bs)
                    dest.write(chunk)
                    size=dest.tell()
                    handler.update(size)
                handler.end(size)

        if os.stat(self.partial_file).st_size == 0:
            os.remove(self.partial_file)

        shutil.move(self.partial_file, self.archive_file)

        return self.archive_file

    def formatRequest(self, request):
        if self.url.auth_info():
            enc = encodestring('%s:%s' % self.url.auth_info())
            request.add_header('Authorization', 'Basic %s' % enc)

        range_handlers = {
            'http' : HTTPRangeHandler,
            'https': HTTPRangeHandler,
            'ftp' : FTPRangeHandler
        }

        if self.exist_size and self.scheme in range_handlers:
            opener = urllib.request.build_opener(range_handlers.get(self.scheme)())
            urllib.request.install_opener(opener)
            request.add_header('Range', 'bytes=%d-' % self.exist_size)

        proxy_handler = None
        # FIXME: Should use __get_proxies function in here
        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            http_proxy = ctx.config.values.general.http_proxy
            proxy_handler = urllib.request.ProxyHandler({URI(http_proxy).scheme(): http_proxy})
        elif ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            https_proxy = ctx.config.values.general.https_proxy
            proxy_handler = urllib.request.ProxyHandler({URI(https_proxy): https_proxy})
        elif ctx.config.values.general.ftp_proxy and self.url.scheme() == "ftp":
            ftp_proxy = ctx.config.values.general.ftp_proxy
            proxy_handler = urllib.request.ProxyHandler({URI(http_proxy): ftp_proxy})
        if proxy_handler:
            ctx.ui.info(_("Proxy configuration has been found for '%s' protocol") % self.url.scheme())
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
        return request

    def _get_http_headers(self):
        headers = []
        if self.url.auth_info() and (self.url.scheme() == "http" or self.url.scheme() == "https"):
            enc = base64.encodestring('%s:%s' % self.url.auth_info())
            headers.append(('Authorization', 'Basic %s' % enc),)
        return tuple(headers)

    def _get_ftp_headers(self):
        headers = []
        if self.url.auth_info() and self.url.scheme() == "ftp":
            enc = base64.encodestring('%s:%s' % self.url.auth_info())
            headers.append(('Authorization', 'Basic %s' % enc),)
        return tuple(headers)

    def _get_proxies(self):
        proxies = {}

        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            proxies[inary.uri.URI(ctx.config.values.general.http_proxy).scheme()] = ctx.config.values.general.http_proxy

        if ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            proxies[inary.uri.URI(ctx.config.values.general.https_proxy).scheme()] = ctx.config.values.general.https_proxy

        if ctx.config.values.general.ftp_proxy and self.url.scheme() == "ftp":
            proxies[inary.uri.URI(ctx.config.values.general.ftp_proxy).scheme()] = ctx.config.values.general.ftp_proxy

        if self.url.scheme() in proxies:
            ctx.ui.info(_("Proxy configuration has been found for '%s' protocol") % self.url.scheme())

        return proxies

    def _get_bandwith_limit(self):
        bandwidth_limit = ctx.config.options.bandwidth_limit or ctx.config.values.general.bandwidth_limit
        if bandwidth_limit and bandwidth_limit != "0":
            ctx.ui.warning(_("Bandwidth usage is limited to %s KB/s") % bandwidth_limit)
            return 1024 * int(bandwidth_limit)
        else:
            return 0

    def _test_range_support(self):
        if not os.path.exists(self.partial_file):
            return None

        try:
            file_obj = urllib.request.urlopen(urllib.request.Request(self.url.get_uri()))
        except urllib.error.URLError:
            ctx.ui.debug(_("Remote file can not be reached. Previously downloaded part of the file will be removed."))
            os.remove(self.partial_file)
            return None

        headers = file_obj.info()
        file_obj.close()
        if 'Content-Length' in headers:
            return 'simple'
        else:
            ctx.ui.debug(_("Server doesn't support partial downloads. Previously downloaded part of the file will be over-written."))
            os.remove(self.partial_file)
            return None

class HTTPRangeHandler(urllib.request.BaseHandler):
    """
    to override the urllib2 error: 'Error 206: Partial Content'
    this reponse from the HTTP server is already what we expected to get.
    Don't give up, resume downloading..
    """
    def http_error_206(self, request, fp, errcode, msg, headers):
        return urllib.addinfourl(fp, headers, request.get_full_url())
    def http_error_416(self, request, fp, errcode, msg, headers):
        # HTTP 1.1's 'Range Not Satisfiable' error..
        raise RangeError 

class FTPRangeHandler(urllib.request.FTPHandler):
    """
    FTP Range support..
    """
    def ftp_open(self, req):
        host = req.get_host()
        host, port = urllib.parse.splitport(host)
        if port is None:
            port = ftplib.FTP_PORT
        try:
            host = socket.gethostbyname(host)
        except socket.error as msg:
            raise FetchError(msg)
        path, attrs = urllib.parse.splitattr(req.get_selector())
        dirs = path.split('/')
        dirs = list(map(urllib.parse.unquote, dirs))
        dirs, file = dirs[:-1], dirs[-1]
        if dirs and not dirs[0]:
            dirs = dirs[1:]
        try:
            fw = self.connect_ftp('', '', host, port, dirs)
            type = file and 'I' or 'D'
            for attr in attrs:
                attr, value = urllib.parse.splitattr(attr)
                if attr.lower() == 'type' and \
                   value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()

            rawr = req.headers.get('Range', None)
            if rawr:
                rest = int(rawr.split("=")[1].rstrip("-"))
            else:
                rest = 0
            fp, retrlen = fw.retrfile(file, type, rest)

            fb, lb = rest, retrlen
            if retrlen is None or retrlen == 0:
                raise RangeError
            retrlen = lb - fb
            if retrlen < 0:
                # beginning of range is larger than file
                raise RangeError

            headers = ''
            mtype = guess_type(req.get_full_url())[0]
            if mtype:
                headers += 'Content-Type: %s\n' % mtype
            if retrlen is not None and retrlen >= 0:
                headers += 'Content-Length: %d\n' % retrlen

            from io import StringIO

            return urllib.addinfourl(fp, Message(StringIO(headers)), req.get_full_url())
        except ftplib.all_errors as msg:
            raise IOError(_('ftp error'), msg).with_traceback(sys.exc_info()[2])

    def connect_ftp(self, user, passwd, host, port, dirs):
        fw = ftpwrapper('', '', host, port, dirs)
        return fw

class ftpwrapper(urllib.request.ftpwrapper):
    def retrfile(self, file, type, rest=None):
        self.endtransfer()
        if type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
        else: cmd = 'TYPE ' + type; isdir = 0
        try:
            self.ftp.voidcmd(cmd)
        except ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)
        conn = None
        if file and not isdir:
            try:
                self.ftp.nlst(file)
            except ftplib.error_perm as reason:
                raise IOError(_('ftp error'), reason).with_traceback(sys.exc_info()[2])
            # Restore the transfer mode!
            self.ftp.voidcmd(cmd)
            try:
                cmd = 'RETR ' + file
                conn = self.ftp.ntransfercmd(cmd, rest)
            except ftplib.error_perm as reason:
                if str(reason)[:3] == '501':
                    # workaround for REST not suported error
                    fp, retrlen = self.retrfile(file, type)
                    fp = RangeableFileObject(fp, (rest,''))
                    return (fp, retrlen)
                elif str(reason)[:3] != '550':
                    raise IOError(_('ftp error'), reason).with_traceback(sys.exc_info()[2])
        if not conn:
            self.ftp.voidcmd('TYPE A')
            if file: cmd = 'LIST ' + file
            else: cmd = 'LIST'
            conn = self.ftp.ntransfercmd(cmd)
        self.busy = 1
        return (urllib.addclosehook(conn[0].makefile('rb'),
                            self.endtransfer), conn[1])
# helper function
def fetch_url(url, destdir, progress=None, destfile=None):
    fetch = Fetcher(url, destdir, destfile)
    fetch.progress = progress
    fetch.fetch()

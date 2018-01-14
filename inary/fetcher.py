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
import urllib.request as urlrequest
import urllib.error as urlerror

#Gettext translation library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# inary modules
import inary
import inary.util as util
import inary.context as ctx
import inary.uri

class FetchError(inary.Error):
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

    def start(self, archive, url, size):
        if os.path.exists(archive):
            self.exist_size = os.path.getsize(archive)
        #self.filename   = util.remove_suffix(ctx.const.partial_suffix, basename)
        self.url        = url
        self.basename   = basename
        self.total_size = size or 0
        self.text       = text

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
                                #filename        = self.filename,
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
        self.headers_dict = {'user-agent' : 'Inary Fetcher/' + inary.__version__,
                             'http-headers' : self._get_http_headers()
                             #'ftp-headers' : self._get_ftp_headers()
                             }


    def test(self, timeout=3):
        try:
            request.urlopen(self.url.get_uri(),
                         proxies=self._get_proxies(),
                         timeout=timeout,
                         headers=headers_dict
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

    def fetch (self):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            raise FetchError(_('Filename error'))

        if not os.access(self.destdir, os.W_OK):
            raise FetchError(_('Access denied to write to destination directory: "%s"') % (self.destdir))

        if os.path.exists(self.archive_file) and not os.access(self.archive_file, os.W_OK):
            raise FetchError(_('Access denied to destination file: "%s"') % (self.archive_file))

        else:
            try:
                with open(self.partial_file, "wb") as f:
                    response = request.urlopen(self.url.get_uri(),
                                        #proxies = self._get_proxies,
                                        headers = self.headers_dict,
                                        verify=None,
                                        stream=True)

                    handler= UIHandler()
                    total_length = int(response.headers.get('content-length'))

                    if total_length is None:  # no content length header
                    # just download the file in one go and fake the progress reporting once done
                        ctx.ui.warning("content-length header is missing for the fetch file, "
                                    "download progress reporting will not be available")
                        f.write(response.content)
                        size = f.tell()
                        handler.start(self.archive_file, self.url.get_uri(), size)
                        handler.end(size)
                    else:
                        handler.start(self.url.get_uri(), total_length)
                        bytes_read = 0
                        for buf in response.iter_content(1024 * 1024):  # 1 MB chunks
                            if buf:
                                f.write(buf)
                                bytes_read += len(buf)
                                handler.update(bytes_read)
                        handler.end(bytes_read)

            except OSError as e:
                raise FetchError(_('Could not fetch destination file "%s":%s') % (self.url.get_uri(), e))

            except request.exceptions.InvalidSchema:
                raise FetchError(_('Package manager not support downloding from ftp mirror'))


        if os.stat(self.partial_file).st_size == 0:
            os.remove(self.partial_file)
            raise FetchError(_('A problem occurred. Please check the archive address and/or permissions again.'))

        shutil.move(self.partial_file, self.archive_file)

        return self.archive_file

    def _get_http_headers(self):
        headers = []
        if self.url.auth_info() and (self.url.scheme() == "http" or self.url.scheme() == "https"):
            enc = base64.encodestring('%s:%s' % self.url.auth_info())
            headers.append(('Authorization', 'Basic %s' % enc),)
        return bytearray(headers)
#
#    def _get_ftp_headers(self):
#        headers = []
#        if self.url.auth_info() and self.url.scheme() == "ftp":
#            enc = base64.encodestring('%s:%s' % self.url.auth_info())
#            headers.append(('Authorization', 'Basic %s' % enc),)
#        return bytearray(headers)

    def _get_proxies(self):
        proxies = {}

        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            proxies[inary.uri.URI(ctx.config.values.general.http_proxy).scheme()] = ctx.config.values.general.http_proxy

        if ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            proxies[inary.uri.URI(ctx.config.values.general.https_proxy).scheme()] = ctx.config.values.general.https_proxy

        #if ctx.config.values.general.ftp_proxy and self.url.scheme() == "ftp":
        #    proxies[inary.uri.URI(ctx.config.values.general.ftp_proxy).scheme()] = ctx.config.values.general.ftp_proxy

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

        import urllib.request, urllib.error, urllib.parse
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


# helper function
def fetch_url(url, destdir, progress=None, destfile=None):
    fetch = Fetcher(url, destdir, destfile)
    fetch.progress = progress
    fetch.fetch()

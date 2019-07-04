# -*- coding: utf-8 -*-

# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Gettext translation library
# python standard library modules
import os
import pycurl
import shutil
import time

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# Network libraries
# import ftplib

# inary modules
import inary
import inary.db
import inary.errors
import inary.util as util
import inary.context as ctx
import inary.uri

from base64 import encodebytes


# For raising errors when fetching
class FetchError(inary.errors.Error):
    pass


# For raising errors when connecting to server
class RangeError(inary.errors.Error):
    pass


# For raising errors when opening files
class FileError(inary.errors.Error):
    pass


# For raising errors when connecting to server
class RemoteError(inary.errors.Error):
    pass


class UIHandler:
    def __init__(self):
        self.filename = None
        self.url = None
        self.basename = None
        self.downloaded_size = 0
        self.percent = None
        self.rate = 0.0
        self.size = 0
        self.eta = '--:--:--'
        self.symbol = '--/-'
        self.last_updated = 0
        self.exist_size = 0

    def start(self, archive, url, basename, size=0):
        if os.path.exists(archive):
            self.exist_size = os.path.getsize(archive)
        self.filename = basename
        self.url = url
        self.basename = basename
        self.total_size = size or 0

        self.now = lambda: time.time()
        self.t_diff = lambda: self.now() - self.s_time

        self.s_time = self.now()

    def update(self, total_to_download, total_downloaded, total_to_upload, total_uploaded):
        if self.size == total_downloaded:
            return

        self.size = total_downloaded
        self.total_size = total_to_download
        if self.total_size:
            try:
                self.percent = (self.size * 100.0) / self.total_size
            except:
                self.percent = 0
        else:
            self.percent = 0

        if int(self.now()) != int(self.last_updated) and self.size > 0:
            try:
                self.rate, self.symbol = util.human_readable_rate(
                    (self.size - self.exist_size) / (self.now() - self.s_time))
            except ZeroDivisionError:
                self.rate, self.symbol = None, None
            if self.total_size:
                self.eta = '%02d:%02d:%02d' % \
                           tuple([i for i in time.gmtime((self.t_diff() * (100 - self.percent)) / self.percent)[3:6]])

        self._update_ui()

    def end(self, read):
        pass

    def _update_ui(self):
        ctx.ui.display_progress(operation="fetching",
                                percent=self.percent,
                                filename=self.filename,
                                total_size=self.total_size or self.size,
                                downloaded_size=self.size,
                                rate=self.rate,
                                eta=self.eta,
                                symbol=self.symbol)

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
        self.c = pycurl.Curl()
        self.archive_file = os.path.join(destdir, destfile or url.filename())
        self.partial_file = os.path.join(self.destdir, self.url.filename()) + ctx.const.partial_suffix

        util.ensure_dirs(self.destdir)

    def fetch(self, timeout=10):
        """Return value: Fetched file's full path.."""

        if not ctx.config.values.general.ssl_verify:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

        if not self.url.filename():
            raise FetchError(_('Filename error'))

        if not os.access(self.destdir, os.W_OK):
            raise FetchError(_('Access denied to write to destination directory: "%s"') % self.destdir)

        if os.path.exists(self.archive_file) and not os.access(self.archive_file, os.W_OK):
            raise FetchError(_('Access denied to destination file: "%s"') % self.archive_file)

        else:
            self.c.protocol = self.url.scheme()
            self.c.setopt(self.c.URL, self.url.get_uri())
            # Some runtime settings (user agent, bandwidth limit, timeout, redirections etc.)
            self.c.setopt(pycurl.MAX_RECV_SPEED_LARGE, self._get_bandwith_limit())
            self.c.setopt(pycurl.USERAGENT, ('Inary Fetcher/' + inary.__version__).encode("utf-8"))
            self.c.setopt(pycurl.AUTOREFERER, 1)
            self.c.setopt(pycurl.CONNECTTIMEOUT, timeout)  # This for waiting to establish connection
            # self.c.setopt(pycurl.TIMEOUT, timeout) # This for waiting to read data
            self.c.setopt(pycurl.MAXREDIRS, 10)
            self.c.setopt(pycurl.NOSIGNAL, True)
            # Header
            # self.c.setopt(pycurl.HTTPHEADER, ["%s: %s" % header for header in self._get_http_headers().items()])

            handler = UIHandler()
            handler.start(self.archive_file, self.url.get_uri(), self.url.filename())

            if os.path.exists(self.partial_file):
                file_id = open(self.partial_file, "ab")
                self.c.setopt(self.c.RESUME_FROM, os.path.getsize(self.partial_file))
                ctx.ui.info(_("Download resuming..."))
            else:
                file_id = open(self.partial_file, "wb")

            # Function sets
            self.c.setopt(pycurl.DEBUGFUNCTION, ctx.ui.debug)
            self.c.setopt(self.c.NOPROGRESS, False)
            self.c.setopt(self.c.XFERINFOFUNCTION, handler.update)

            self.c.setopt(pycurl.FOLLOWLOCATION, 1)
            self.c.setopt(self.c.WRITEDATA, file_id)

            try:
                self.c.perform()
                file_id.close()
                ctx.ui.info("\n")
                ctx.ui.debug(_("Downloaded from:" + str(self.c.getinfo(self.c.EFFECTIVE_URL))))
                self.c.close()
            except pycurl.error as x:
                raise FetchError("Pycurl.Error: {}".format(x))

        if os.stat(self.partial_file).st_size == 0:
            os.remove(self.partial_file)
            ctx.ui.error(
                FetchError(_('A problem occurred. Please check the archive address and/or permissions again.')))

        shutil.move(self.partial_file, self.archive_file)

        return self.archive_file

    def _get_http_headers(self):
        headers = []
        if self.url.auth_info() and (self.url.scheme() == "http" or self.url.scheme() == "https"):
            enc = encodebytes('{0}:{0}'.format(self.url.auth_info()).encode('utf-8'))
            headers.append(('Authorization', 'Basic {}'.format(enc)))
        return headers

    def _get_ftp_headers(self):
        headers = []
        if self.url.auth_info() and self.url.scheme() == "ftp":
            enc = encodebytes('{0}:{0}'.format(self.url.auth_info()).encode('utf-8'))
            headers.append(('Authorization', 'Basic {}'.format(enc)))
        return headers

    def _get_proxies(self):
        proxies = {}

        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            proxies[inary.uri.URI(ctx.config.values.general.http_proxy).scheme()] = ctx.config.values.general.http_proxy

        if ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            proxies[
                inary.uri.URI(ctx.config.values.general.https_proxy).scheme()] = ctx.config.values.general.https_proxy

        if ctx.config.values.general.ftp_proxy and self.url.scheme() == "ftp":
            proxies[inary.uri.URI(ctx.config.values.general.ftp_proxy).scheme()] = ctx.config.values.general.ftp_proxy

        if self.url.scheme() in proxies:
            ctx.ui.info(_("Proxy configuration has been found for '{}' protocol").format(self.url.scheme()))

        return proxies

    @staticmethod
    def _get_bandwith_limit():
        bandwidth_limit = ctx.config.options.bandwidth_limit or ctx.config.values.general.bandwidth_limit
        if bandwidth_limit and bandwidth_limit != "0":
            ctx.ui.warning(_("Bandwidth usage is limited to {} KB/s").format(bandwidth_limit))
            return 1024 * int(bandwidth_limit)
        else:
            return 0


# helper function
def fetch_url(url, destdir, progress=None, destfile=None):
    fetch = Fetcher(url, destdir, destfile)
    fetch.progress = progress
    fetch.fetch()


# Operation function
def fetch(packages=None, path=os.path.curdir):
    """
    Fetches the given packages from the repository without installing, just downloads the packages.
    @param packages: list of package names -> list_of_strings
    @param path: path to where the packages will be downloaded. If not given, packages will be downloaded
    to the current working directory.
    """
    if packages is None:
        packages = []
    packagedb = inary.db.packagedb.PackageDB()
    repodb = inary.db.repodb.RepoDB()
    for name in packages:
        package, repo = packagedb.get_package_repo(name)
        ctx.ui.info(_("{0} package found in {1} repository").format(package.name, repo))
        uri = inary.uri.URI(package.packageURI)
        output = os.path.join(path, uri.path())
        if os.path.exists(output) and package.packageHash == inary.util.sha1_file(output):
            ctx.ui.warning(_("{} package already fetched").format(uri.path()))
            continue
        if uri.is_absolute_path():
            url = str(uri.path())
        else:
            url = os.path.join(os.path.dirname(repodb.get_repo_url(repo)), str(uri.path()))

        fetch_url(url, path, ctx.ui.Progress)

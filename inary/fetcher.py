#-*- coding: utf-8 -*-

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

# python standard library modules
import os
import sys
import time
import shutil

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


# Network libraries
# import ftplib

#Gettext translation library


# inary modules
import inary
import inary.db
import inary.errors
import inary.util as util
import inary.context as ctx
import inary.uri

# requests

try:
    import requests
except ImportError:
    sys.stdout.write(inary.util.colorize(_("ERROR:\n"),"blinkingred")+ \
                     _("\tCan't imported requests module.\n"
                       "\tWhether want the download packages please install\n"
                       "\t'python3-requests' package from repository.\n"))
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
        self.headers_dict = {'user-agent' : 'Inary Fetcher/' + inary.__version__,
                             'http-headers' : self._get_http_headers(),
                             'ftp-headers' : self._get_ftp_headers()
                             }


    def test(self, timeout=3):
        try:
            requests.get(self.url.get_uri(),
                           proxies=self._get_proxies(),
                           timeout=timeout,
                           headers=self.headers_dict
                           )

        except ValueError as e:
            msg = _("Url Problem: \n {}").format(e)
            raise FetchError(msg)

        except FetchError as e:
            msg = _("Can not avaible remote server: \n {}").format(e)
            raise FetchError(msg)


        return True

    def fetch(self, verify=None):
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
                    response = requests.get(self.url.get_uri(),
                                        proxies = self._get_proxies(),
                                        headers = self.headers_dict,
                                        verify  = verify,
                                        timeout = 5,
                                        stream  = True)

                    handler= UIHandler()
                    total_length = response.headers.get('content-length')

                    if total_length is None:  # no content length header
                    # just download the file in one go and fake the progress reporting once done
                        ctx.ui.warning("Content-length header is missing for the fetch file, Download progress reporting will not be available")
                        size=f.tell()
                        handler.start(self.archive_file, self.url.get_uri(), self.url.filename(), size)
                        for buf in response.iter_content(1024 * 1024):  # 1 MB chunks
                            f.write(buf)
                            size=f.tell()
                            handler.update(size)
                        handler.end(size)

                    else:
                        handler.start(self.archive_file, self.url.get_uri(),self.url.filename(), int(total_length))
                        bytes_read = 0
                        for buf in response.iter_content(1024 * 1024):  # 1 MB chunks
                            if buf:
                                f.write(buf)
                                bytes_read += len(buf)
                                handler.update(bytes_read)
                        handler.end(bytes_read)

            except OSError as e:
                raise FetchError(_('Could not fetch destination file "%s":%s') % (self.url.get_uri(), e))

            except requests.exceptions.InvalidSchema:
                # TODO: Add ftp downloader with ftplib
                raise FetchError(_('Package manager not support downloding from ftp mirror'))

            except requests.exceptions.MissingSchema:
                ctx.ui.info(_("Copying local file {}").format(self.url.get_uri()))
                shutil.copy(self.url.get_uri(), self.partial_file)

        if os.stat(self.partial_file).st_size == 0:
            os.remove(self.partial_file)
            raise FetchError(_('A problem occurred. Please check the archive address and/or permissions again.'))

        shutil.move(self.partial_file, self.archive_file)

        return self.archive_file

    def _get_http_headers(self):
        headers = []
        if self.url.auth_info() and (self.url.scheme() == "http" or self.url.scheme() == "https"):
            enc = encodebytes('{0}:{0}'.format(self.url.auth_info()).encode('utf-8'))
            headers.append(('Authorization', 'Basic {}'.format(enc)))
        return str(headers)

    def _get_ftp_headers(self):
        headers = []
        if self.url.auth_info() and self.url.scheme() == "ftp":
            enc = encodesbytes('{0}:{0}'.format(self.url.auth_info()).encode('utf-8'))
            headers.append(('Authorization', 'Basic {}'.format(enc)))
        return str(headers)

    def _get_proxies(self):
        proxies = {}

        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            proxies[inary.uri.URI(ctx.config.values.general.http_proxy).scheme()] = ctx.config.values.general.http_proxy

        if ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            proxies[inary.uri.URI(ctx.config.values.general.https_proxy).scheme()] = ctx.config.values.general.https_proxy

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
            url = str(pkg_uri)
        else:
            url = os.path.join(os.path.dirname(repodb.get_repo_url(repo)), str(uri.path()))

        fetch_url(url, path, ctx.ui.Progress)

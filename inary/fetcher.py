# -*- coding: utf-8 -*-

# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standard Python Modules
import os
import time
import random
import shutil
from base64 import encodebytes

# INARY Modules
import inary
import inary.db
import inary.uri
import inary.errors
import inary.mirrors
from inary import util
from inary.util import ctx

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


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
        self.pkgname = None
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

    def update(self, total_to_download, total_downloaded,
               total_to_upload=0, total_uploaded=0,
               background_color=None, foreground_color=None):
        if self.size == total_downloaded:
            return

        self.size = total_downloaded
        self.total_size = total_to_download
        self.background = background_color
        self.foreground = foreground_color
        if self.total_size:
            try:
                self.percent = (self.size * 100.0) / self.total_size
            except BaseException:
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
                           tuple([i for i in time.gmtime(
                               (self.t_diff() * (100 - self.percent)) / self.percent)[3:6]])

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
                                symbol=self.symbol,
                                basename=self.basename,
                                backgroundcolor=self.background,
                                foregroundcolor=self.foreground)

        self.last_updated = self.now()


class Fetcher:
    """Fetcher can fetch a file from various sources using various
    protocols."""

    FETCH_MODE_PYCURL = 1
    FETCH_MODE_REQUESTS = 2
    FETCH_MODE_WGET = 3

    def __init__(self, url, destdir="/tmp", destfile=None):
        if not isinstance(url, inary.uri.URI):
            url = inary.uri.URI(url)

        if ctx.config.get_option("authinfo"):
            url.set_auth_info(ctx.config.get_option("authinfo"))

        self.url = url
        self.destdir = destdir
        self.destfile = destfile
        self.progress = None
        self.try_number = 0
        self.fetcher = None
        self.handler = None

        # spoof user-agent
        self.useragent = (ctx.config.values.general.fetcher_useragent
                          or 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')

        self.archive_file = os.path.join(destdir, destfile or url.filename())
        self.partial_file = os.path.join(
            self.destdir, self.url.filename()) + ctx.const.partial_suffix
        util.ensure_dirs(self.destdir)

    def fetch(self, timeout=30):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            raise FetchError(_('Filename error'))

        if not os.access(self.destdir, os.W_OK):
            raise FetchError(
                _('Access denied to write to destination directory: "{}"').format(
                    self.destdir))

        if os.path.exists(self.archive_file) and not os.access(
                self.archive_file, os.W_OK):
            raise FetchError(
                _('Access denied to destination file: "{}"').format(
                    self.archive_file))

        if os.path.exists(self.archive_file):
            ctx.ui.info(
                _("File already exsist. Download skiped..."),
                verbose=True)
            return 0

        if os.path.exists(self.partial_file):
            os.remove(self.partial_file)

        self.file_id = open(self.partial_file, "wb")

        try:
            self.fetcher = self._get_fetcher_mode()
            if self.fetcher_mode != self.FETCH_MODE_WGET and not self.handler:
                self.handler = UIHandler()
                self.handler.start(
                    self.archive_file,
                    self.url.get_uri(),
                    self.url.filename())
            self.timeout = timeout
            self.fetcher()
        except Exception as x:
            if x.args[0] == 33:
                os.remove(self.partial_file)
            if self.try_number != 3:
                self.try_number = self.try_number + 1
                ctx.ui.info(_("Download error: {}".format(x)), verbose=True)
                fetch()
            raise x
            # raise FetchError("{}".format(x.args[1]))

        if os.stat(self.partial_file).st_size == 0:
            os.remove(self.partial_file)
            ctx.ui.error(
                FetchError(_('A problem occurred. Please check the archive address and/or permissions again.')))

        shutil.move(self.partial_file, self.archive_file)
        return self.archive_file

    def _get_pycurl(self):
        import pycurl
        c = pycurl.Curl()
        c.protocol = self.url.scheme()
        c.setopt(c.URL, self.url.get_uri())
        # Some runtime settings (user agent, bandwidth limit, timeout,
        # redirections etc.)
        c.setopt(pycurl.MAX_RECV_SPEED_LARGE, self._get_bandwith_limit())
        c.setopt(pycurl.USERAGENT, (self.useragent).encode("utf-8"))
        c.setopt(pycurl.AUTOREFERER, 1)
        # This for waiting to establish connection
        c.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
        # c.setopt(pycurl.TIMEOUT, timeout) # This for waiting to read data
        c.setopt(pycurl.MAXREDIRS, 50)
        c.setopt(pycurl.NOSIGNAL, True)
        if hasattr(pycurl, "AUTOREFERER"):
            c.setopt(pycurl.AUTOREFERER, 1)

        c.setopt(pycurl.LOW_SPEED_TIME, 30)
        c.setopt(pycurl.LOW_SPEED_LIMIT, 5)

        if not ctx.config.values.general.ssl_verify:
            c.setopt(pycurl.SSL_VERIFYPEER, 0)
            c.setopt(pycurl.SSL_VERIFYHOST, 0)
        else:
            # To block man-in-middle attack
            c.setopt(pycurl.SSL_VERIFYHOST, 2)
            # c.setopt(pycurl.CAINFO, "/etc/inary/certificates/sourceforge.crt")

        # Header
        # c.setopt(pycurl.HTTPHEADER, ["%s: %s" % header for header in self._get_http_headers().items()])
        # Function sets
        c.setopt(pycurl.DEBUGFUNCTION, ctx.ui.debug)
        c.setopt(c.NOPROGRESS, False)
        c.setopt(c.XFERINFOFUNCTION, self.handler.update)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(c.WRITEDATA, self.file_id)
        c.perform()
        # This is not a bug. This is a new feature. ŞAka bir yana bu hata
        ctx.ui.info("\n", noln=True)
        # pycurl yüzünden kaynaklanıyor
        self.file_id.close()
        ctx.ui.info(_("RESPONSE: ") +
                    str(c.getinfo(c.RESPONSE_CODE)), verbose=True)
        ctx.ui.info(_("Downloaded from: " +
                      str(c.getinfo(c.EFFECTIVE_URL))), verbose=True)
        c.close()

    def _get_wget(self):
        return os.system("timeout \"{}\" busybox wget -c --user-agent \"{}\"  \"{}\" -O \"{}\" 2>&1".format(self.timeout, self.useragent, self.url.get_uri(), self.partial_file))

    def _get_requests(self):
        from requests import get
        c = get(self.url.get_uri(), stream=True, timeout=self.timeout, headers={
                'User-Agent': self.useragent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'SEC-FETCH-DEST': 'document',
                'SEC-FETCH-MODE': 'navigate',
                'SEC-FETCH-SITE': 'none',
                'SEC-FETCH-USER': '?1',
                'UPGRADE-INSECURE-REQUESTS': '1'
                }
                )
        total = c.headers.get('content-length')
        if not total:
            self.file_id.write(c.content)
        else:
            down = 0
            total = int(total)
            chunk = int(ctx.config.values.general.fetcher_chunksize or 8196)
            for data in c.iter_content(chunk_size=chunk):
                self.file_id.write(data)
                down += len(data)
                self.handler.update(
                    total, down, foreground_color="backgroundblue")
        ctx.ui.info("\n", noln=True)
        self.file_id.close()

    def _get_fetcher_mode(self):
        if not self.fetcher:
            mode = int(ctx.config.values.general.fetcher_mode or 0)
            self.fetcher_mode = mode
            if mode not in [self.FETCH_MODE_PYCURL, self.FETCH_MODE_REQUESTS, self.FETCH_MODE_WGET]:
                try:
                    from pycurl import URL
                    self.fetcher = self._get_pycurl
                    self.fetcher_mode = self.FETCH_MODE_PYCURL
                except ImportError:
                    try:
                        from requests import get
                        self.fetcher = self._get_requests
                        self.fetcher_mode = self.FETCH_MODE_REQUESTS
                    except ImportError:
                        self.fetcher = self._get_wget
                        self.fetcher_mode = self.FETCH_MODE_WGET

            elif mode == 1:
                self.fetcher = self._get_pycurl
            elif mode == 2:
                self.fetcher = self._get_requests
            elif mode == 3:
                self.fetcher = self._get_wget

        return self.fetcher

    def _get_http_headers(self):
        headers = []
        if self.url.auth_info() and (self.url.scheme() ==
                                     "http" or self.url.scheme() == "https"):
            enc = encodebytes(
                '{0}:{0}'.format(
                    self.url.auth_info()).encode('utf-8'))
            headers.append(('Authorization', 'Basic {}'.format(enc)))
        return headers

    def _get_ftp_headers(self):
        headers = []
        if self.url.auth_info() and self.url.scheme() == "ftp":
            enc = encodebytes(
                '{0}:{0}'.format(
                    self.url.auth_info()).encode('utf-8'))
            headers.append(('Authorization', 'Basic {}'.format(enc)))
        return headers

    def _get_proxies(self):
        proxies = {}

        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            proxies[inary.uri.URI(ctx.config.values.general.http_proxy).scheme(
            )] = ctx.config.values.general.http_proxy

        if ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            proxies[
                inary.uri.URI(ctx.config.values.general.https_proxy).scheme()] = ctx.config.values.general.https_proxy

        if ctx.config.values.general.ftp_proxy and self.url.scheme() == "ftp":
            proxies[inary.uri.URI(ctx.config.values.general.ftp_proxy).scheme(
            )] = ctx.config.values.general.ftp_proxy

        if self.url.scheme() in proxies:
            ctx.ui.info(
                _("Proxy configuration has been found for '{}' protocol.").format(
                    self.url.scheme()))

        return proxies

    @staticmethod
    def _get_bandwith_limit():
        bandwidth_limit = ctx.config.options.bandwidth_limit or ctx.config.values.general.bandwidth_limit
        if bandwidth_limit and bandwidth_limit != "0":
            ctx.ui.warning(
                _("Bandwidth usage is limited to {} KB/s.").format(bandwidth_limit))
            return 1024 * int(bandwidth_limit)
        else:
            return 0

    def _test_range_support(self):
        if not os.path.exists(self.partial_file):
            return False

        import urllib.request
        try:
            file_obj = urllib.request.urlopen(self.url.get_uri())
        except urllib.request.URLError:
            ctx.ui.debug(
                _("Remote file can not be reached. Previously downloaded part of the file will be removed."))
            os.remove(self.partial_file)
            return False

        headers = file_obj.info()
        file_obj.close()
        if headers.get("Content-Length"):
            return True
        else:
            ctx.ui.debug(
                _("Server doesn't support partial downloads. Previously downloaded part of the file will be over-written."))
            os.remove(self.partial_file)
            return False


# helper function
def fetch_git(url, destdir="", branch="master"):
    if os.path.isdir(destdir):
        os.system("rm -rf \"{}\"".format(destdir))
    status = os.system(
        "git clone  \"{0}\" \"{1}\" -b \"{2}\"".format(url, destdir, branch))
    if status != 0:
        print(status)
        ctx.ui.error(
            _('Failed to clone git repository from {}.').format(url))
        exit(1)


def fetch_url(url, destdir=None, progress=None, destfile=None, pkgname=''):

    if not destdir:
        destdir = ctx.config.archives_dir()
    if not progress:
        progress = ctx.ui.Progress
    if "mirrors://" in str(url):
        fetch_from_mirror(str(url), destdir, progress, destfile)
    else:
        fetch = Fetcher(url, destdir, destfile)
        fetch.progress = progress
        fetch.fetch()


def fetch_from_fallback(url, destdir=None, progress=None, destfile=None):
    archive = os.path.basename(url)
    src = os.path.join(ctx.config.values.build.fallback, archive)
    ctx.ui.warning(_('Trying fallback address: \"{}\"').format(src))
    fetch_url(src, destdir=destdir, progress=progress, destfile=destfile)


def fetch_from_locale(url, destdir=None, progress=None, destfile=None):
    if not destdir:
        destdir = ctx.config.archives_dir()
    if url.startswith("file://"):
        url = url[7:]
    if not os.access(url, os.F_OK):
        raise FetchError(
            _('No such file or no permission to read for {}.').format(url))
    shutil.copy(url, os.path.join(destdir, destfile or url.split("/")[-1]))


def fetch_from_mirror(url, destdir=None, progress=None, destfile=None):
    sep = url[len("mirrors://"):].split("/")
    name = sep.pop(0)
    archive = "/".join(sep)

    mirrors = inary.mirrors.Mirrors().get_mirrors(name)
    random.shuffle(mirrors)  # randomize mirror list
    if not mirrors:
        raise inary.mirrors.MirrorError(
            _("\"{}\" mirrors are not defined.").format(name))

    for mirror in mirrors:
        try:
            mirror_url = os.path.join(mirror, archive)
            ctx.ui.debug(_('Fetching source from: \"{}\"').format(mirror_url))
            fetch_url(
                mirror_url,
                destdir=destdir,
                progress=progress,
                destfile=destfile)
            return
        except FetchError:
            pass

    raise FetchError(
        _('Could not fetch source from \"{}\" mirrors.').format(name))

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
        ctx.ui.info(
            _("\"{0}\" package found in \"{1}\" repository.").format(
                package.name, repo))
        uri = inary.uri.URI(package.packageURI)
        output = os.path.join(path, uri.path())
        if os.path.exists(
                output) and package.packageHash == inary.util.sha1_file(output):
            ctx.ui.warning(
                _("\"{}\" package already fetched.").format(
                    uri.path()))
            continue
        if uri.is_absolute_path():
            url = str(uri.path())
        else:
            url = os.path.join(
                os.path.dirname(
                    repodb.get_repo_url(repo)), str(
                    uri.path()))

        if url.startswith("git://") or url.endswith(".git"):
            branch = "master"
            fetch_git(url.replace("git://", "https://"), path, branch)
        elif "://" in url:
            fetch_url(url, path, ctx.ui.Progress)
        else:
            fetch_from_locale(url, path)

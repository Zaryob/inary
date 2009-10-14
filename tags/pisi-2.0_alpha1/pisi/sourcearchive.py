# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# python standard library

import os
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# pisi modules
import pisi
import pisi.util as util
import pisi.context as ctx
import pisi.archive
import pisi.uri
import pisi.fetcher
import pisi.mirrors

class Error(pisi.Error):
    pass

class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, spec, pkg_work_dir):
        self.url = pisi.uri.URI(spec.source.archive.uri)
        self.pkg_work_dir = pkg_work_dir
        self.archiveFile = os.path.join(ctx.config.archives_dir(), self.url.filename())
        self.archive = spec.source.archive

    def fetch(self, interactive=True):
        if not self.is_cached(interactive):
            if interactive:
                self.progress = ctx.ui.Progress
            else:
                self.progress = None

            try:
                if self.url.get_uri().startswith("mirrors://"):
                    self.fetch_from_mirror()
                else:
                    pisi.fetcher.fetch_url(self.url, ctx.config.archives_dir(), self.progress)
            except pisi.fetcher.FetchError:
                if ctx.config.values.build.fallback:
                    self.fetch_from_fallback()
                else:
                    raise

    def fetch_from_fallback(self):
        archive = os.path.basename(self.url.get_uri())
        src = os.path.join(ctx.config.values.build.fallback, archive)
        ctx.ui.warning(_('Trying fallback address: %s') % src)
        pisi.fetcher.fetch_url(src, ctx.config.archives_dir(), self.progress)

    def fetch_from_mirror(self):
        uri = self.url.get_uri()
        sep = uri[len("mirrors://"):].split("/")
        name = sep.pop(0)
        archive = "/".join(sep)

        mirrors = pisi.mirrors.Mirrors().get_mirrors(name)
        if not mirrors:
            raise Error(_("%s mirrors are not defined.") % name)

        for mirror in mirrors:
            try:
                url = os.path.join(mirror, archive)
                ctx.ui.warning(_('Fetching source from mirror: %s') % url)
                pisi.fetcher.fetch_url(url, ctx.config.archives_dir(), self.progress)
                return
            except pisi.fetcher.FetchError:
                pass

        raise pisi.fetcher.FetchError(_('Could not fetch source from %s mirrors.') % name);

    def is_cached(self, interactive=True):
        if not os.access(self.archiveFile, os.R_OK):
            return False

        # check hash
        if util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            if interactive:
                ctx.ui.info(_('%s [cached]') % self.archive.name)
            return True

        return False

    def unpack(self, clean_dir=True):

        # check archive file's integrity
        if not util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            raise Error, _("unpack: check_file_hash failed")

        archive = pisi.archive.Archive(self.archiveFile, self.archive.type)
        archive.unpack(self.pkg_work_dir, clean_dir)

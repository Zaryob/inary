# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors: Baris Metin <baris@uludag.org.tr>
#          Eray Ozkural <eray@uludag.org.tr>

# python standard library

from os.path import join
from os import access, R_OK


# pisi modules
import pisi
import pisi.util as util
import pisi.context as ctx
from pisi.archive import Archive
from pisi.uri import URI
from pisi.fetcher import fetch_url

class SourceArchiveError(pisi.Error):
    pass

class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, bctx):
        self.url = URI(bctx.spec.source.archiveUri)
        self.archiveFile = join(ctx.config.archives_dir(), self.url.filename())
        self.archiveName = bctx.spec.source.archiveName
        self.archiveType = bctx.spec.source.archiveType
        self.archiveSHA1 = bctx.spec.source.archiveSHA1
        self.bctx = bctx

    def fetch(self, interactive=True):
        if not self.is_cached(interactive):
            if interactive:
                progress = ctx.ui.Progress
            else: progress = None
            fetch_url(self.url, ctx.config.archives_dir(), progress)
        
    def is_cached(self, interactive=True):
        if not access(self.archiveFile, R_OK):
            return False

        # check hash
        if util.check_file_hash(self.archiveFile, self.archiveSHA1):
            if interactive:
                ctx.ui.info('%s [cached]' % self.archiveName)
            return True

        return False

    def unpack(self, cleanDir=True):

        # check archive file's integrity
        if not util.check_file_hash(self.archiveFile, self.archiveSHA1):
            raise SourceArchiveError, "unpack: check_file_hash failed"
            
        archive = Archive(self.archiveFile, self.archiveType)
        archive.unpack(self.bctx.pkg_work_dir(), cleanDir)

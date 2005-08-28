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

# python standard library

# Authors: Baris Metin <baris@uludag.org.tr
#          Eray Ozkural <eray@uludag.org.tr>

from os.path import join
from os import access, R_OK


# pisi modules
import pisi
from pisi.archive import Archive
from pisi.uri import URI
from pisi.fetcher import fetch_url
import pisi.util as util

class SourceArchiveError(pisi.Error):
    pass

class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, ctx):
        self.ctx = ctx
        self.url = URI(self.ctx.spec.source.archiveUri)
        self.archiveFile = join(config.archives_dir(), self.url.filename())
        self.archiveType = self.ctx.spec.source.archiveType
        self.archiveSHA1 = self.ctx.spec.source.archiveSHA1

    def fetch(self, interactive=True):
        if not self.is_cached(interactive):
            if interactive:
                progress = ui.Progress
            else: progress = None
            fetch_url(self.url, config.archives_dir(), progress)
        
    def is_cached(self, interactive=True):
        if not access(self.archiveFile, R_OK):
            return False

        # check hash
        if util.check_file_hash(self.archiveFile, self.archiveSHA1):
            if interactive:
                ui.info('%s [cached]\n' % self.ctx.spec.source.archiveName)
            return True

        return False

    def unpack(self, cleanDir=True):

        # check archive file's integrity
        if not util.check_file_hash(self.archiveFile, self.archiveSHA1):
            raise SourceArchiveError, "unpack: check_file_hash failed"
            
        archive = Archive(self.archiveFile, self.archiveType)
        archive.unpack(self.ctx.pkg_work_dir(), cleanDir)

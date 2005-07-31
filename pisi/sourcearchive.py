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
from archive import Archive
from purl import PUrl
from ui import ui
from config import config
from fetcher import fetchUrl
import util


class SourceArchiveError(Exception):
    pass

class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, ctx):
        self.ctx = ctx
        self.url = PUrl(self.ctx.spec.source.archiveUri)
        self.dest = join(config.archives_dir(), self.url.filename())

    def fetch(self, interactive=True):
        if not self.isCached(interactive):
            if interactive:
                progress = ui.Progress
            else: progress = None
            fetchUrl(self.url, config.archives_dir(), progress)
        
    def isCached(self, interactive=True):
        if not access(self.dest, R_OK):
            return False

        # check hash
        if util.sha1_file(self.dest) == self.ctx.spec.source.archiveSHA1:
            if interactive:
                ui.info('%s [cached]\n' % self.ctx.spec.source.archiveName)
            return True

        return False

    def unpack(self, cleanDir=True):
        archive = Archive(self.dest, self.ctx.spec.source.archiveType)
        archive.unpack(self.ctx.pkg_work_dir(), cleanDir)

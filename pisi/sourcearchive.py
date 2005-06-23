# python standard library
import os
import sys


# pisi modules
from fetcher import Fetcher
from archive import Archive
import util
from ui import ui
import context

class SourceArchiveError(Exception):
    pass

class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, ctx):
        self.ctx = ctx
        self.fileName = os.path.basename(self.ctx.spec.source.archiveUri)
        self.filePath = os.path.join(self.ctx.archives_dir(), self.fileName)

    def unpack(self):
        archive = Archive(self.filePath, self.ctx.spec.source.archiveType)
        archive.unpack(self.ctx.pkg_work_dir())

    def displayProgress(pd):
        out = '\r%-30.30s %3d%% %12.2f %s' % \
              (pd['filename'], pd['percent'], pd['rate'], pd['symbol'])
        ui.info(out)

    def fetch(self, percentHook=displayProgress):
        """fetch an archive and store to ctx.archives_dir() 
        using fetcher.Fetcher"""
        fetch = Fetcher(self.ctx.spec.source)

        # check if source already cached
        destpath = fetch.filedest + "/" + fetch.filename
        if os.access(destpath, os.R_OK):
            if util.sha1_file(destpath) == self.ctx.spec.source.archiveSHA1:
                ui.info('%s [cached]\n' % self.ctx.spec.source.archiveName)
                return

        if percentHook:
            fetch.percentHook = percentHook
        
        fetch.fetch()

        # FIXME: What a ugly hack! We should really find a cleaner way for output.
        if percentHook:
            ui.info('\n')
            pass

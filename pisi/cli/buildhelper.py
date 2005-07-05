# -*- coding: utf-8 -*-

from os.path import basename, dirname, join

from pisi.ui import ui
from pisi.context import BuildContext
from pisi.config import config
from pisi.constants import const
from pisi.build import PisiBuild, PisiBuildError
from pisi.purl import PUrl
from pisi.fetcher import fetchUrl

class RemoteSource(object):
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.location = dirname(self.url.uri)

        pkgname = basename(dirname(self.url.path()))
        self.dest = join(config.tmp_dir(), pkgname)
        
        self.fetch_pspec()
        pspec = join(self.dest, self.url.filename())
        self.ctx = BuildContext(pspec)

        self.fetch_actionsfile()
        self.fetch_patches()
        self.fetch_additionalFiles()

    def fetch_pspec(self):
        self.fetchFile(self.url.uri)

    def fetch_actionsfile(self):
        actionsuri = join(self.location, const.actions_file)
        self.fetchFile(actionsuri)
        
    def fetch_patches(self):
        spec = self.ctx.spec
        for patch in spec.source.patches:
            patchuri = join(self.location, 
                            const.files_dir, patch.filename)
            self.fetchFile(patchuri, const.files_dir)

    def fetch_additionalFiles(self):
        spec = self.ctx.spec
        for afile in spec.source.additionalFiles:
            afileuri = join(self.location, 
                            const.files_dir, patch.filename)
            self.fetchFile(afileuri, const.files_dir)

    def fetchFile(self, uri, appendDest=""):
        ui.info("Fetching %s\n" % uri)
        dest = join(self.dest, appendDest)
        fetchUrl(uri, dest,
                 username=self.username,
                 password=self.password)


def build(pspecfile, username=None, password=None):
    # What we need to do first is create a context with our specfile
    url = PUrl(pspecfile)
    if url.isRemoteFile():
        rs = RemoteSource(url, username, password)
        ctx = rs.ctx
    else:
        ctx = BuildContext(url.uri)
    # don't do the real job here. this is just a CLI!
    pb = PisiBuild(ctx)
    pb.build()

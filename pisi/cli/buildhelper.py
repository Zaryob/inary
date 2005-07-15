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
    def __init__(self, url, authInfo=None):
        self.url = url
        if authInfo:
            self.url.setAuthInfo(authInfo)
        self.location = dirname(self.url.uri)

        pkgname = basename(dirname(self.url.path()))
        self.dest = join(config.tmp_dir(), pkgname)
        
        # fetch pspec file
        self.fetch()
        pspec = join(self.dest, self.url.filename())
        self.ctx = BuildContext(pspec)

        self.fetch_actionsfile()
        self.fetch_patches()
        self.fetch_comarfiles()
        self.fetch_additionalFiles()


    def fetch_actionsfile(self):
        actionsuri = join(self.location, const.actions_file)
        self.url.uri = actionsuri
        self.fetch()
        
    def fetch_patches(self):
        spec = self.ctx.spec
        for patch in spec.source.patches:
            patchuri = join(self.location, 
                            const.files_dir, patch.filename)
            self.url.uri = patchuri
            self.fetch(const.files_dir)

    def fetch_comarfiles(self):
        spec = self.ctx.spec
        for package in spec.packages:
            for pcomar in package.providesComar:
                comaruri = join(self.location,
                                const.comar_dir, pcomar.script)
                self.url.uri = comaruri
                self.fetch(const.comar_dir)

    def fetch_additionalFiles(self):
        spec = self.ctx.spec
        for afile in spec.source.additionalFiles:
            afileuri = join(self.location, 
                            const.files_dir, patch.filename)
            self.url.uri = afileuri
            self.fetch(const.files_dir)

    def fetch(self, appendDest=""):
        ui.info("Fetching %s\n" % self.url.uri)
        dest = join(self.dest, appendDest)
        fetchUrl(self.url, dest)

def build(pspecfile, authInfo=None):
    # What we need to do first is create a context with our specfile
    url = PUrl(pspecfile)
    if url.isRemoteFile():
        rs = RemoteSource(url, authInfo)
        ctx = rs.ctx
    else:
        ctx = BuildContext(url.uri)
    # don't do the real job here. this is just a CLI!
    pb = PisiBuild(ctx)
    pb.build()

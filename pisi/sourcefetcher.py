# -*- coding: utf-8 -*-

from os.path import basename, dirname, join

from ui import ui
from config import config
from constants import const
from purl import PUrl
from specfile import SpecFile

class SourceFetcher(object):
    def __init__(self, url, authInfo=None):
        self.url = url
        if authInfo:
            self.url.setAuthInfo(authInfo)
        self.location = dirname(self.url.uri)

        pkgname = basename(dirname(self.url.path()))
        self.dest = join(config.tmp_dir(), pkgname)
        
    def fetch_all(self):
        # fetch pspec file
        self.fetch()
        pspec = join(self.dest, self.url.filename())
        self.spec = SpecFile()
        self.spec.read(pspec)

        self.fetch_actionsfile()
        self.fetch_patches()
        self.fetch_comarfiles()
        self.fetch_additionalFiles()

        return pspec

    def fetch_actionsfile(self):
        actionsuri = join(self.location, const.actions_file)
        self.url.uri = actionsuri
        self.fetch()
        
    def fetch_patches(self):
        spec = self.spec
        for patch in spec.source.patches:
            patchuri = join(self.location, 
                            const.files_dir, patch.filename)
            self.url.uri = patchuri
            self.fetch(const.files_dir)

    def fetch_comarfiles(self):
        spec = self.spec
        for package in spec.packages:
            for pcomar in package.providesComar:
                comaruri = join(self.location,
                                const.comar_dir, pcomar.script)
                self.url.uri = comaruri
                self.fetch(const.comar_dir)

    def fetch_additionalFiles(self):
        spec = self.spec
        for afile in spec.source.additionalFiles:
            afileuri = join(self.location, 
                            const.files_dir, patch.filename)
            self.url.uri = afileuri
            self.fetch(const.files_dir)

    def fetch(self, appendDest=""):
        from fetcher import fetchUrl

        ui.info("Fetching %s\n" % self.url.uri)
        dest = join(self.dest, appendDest)
        fetchUrl(self.url, dest)


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

from os.path import basename, dirname, join

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
from pisi.uri import URI
from pisi.specfile import SpecFile

class SourceFetcher(object):
    def __init__(self, url, authInfo=None):
        self.url = url
        if authInfo:
            self.url.set_auth_info(authInfo)
        self.location = dirname(self.url.uri)

        pkgname = basename(dirname(self.url.path()))
        self.dest = join(ctx.config.tmp_dir(), pkgname)
        
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
        actionsuri = join(self.location, ctx.const.actions_file)
        self.url.uri = actionsuri
        self.fetch()
        
    def fetch_patches(self):
        spec = self.spec
        for patch in spec.source.patches:
            patchuri = join(self.location, 
                            ctx.const.files_dir, patch.filename)
            self.url.uri = patchuri
            self.fetch(ctx.const.files_dir)

    def fetch_comarfiles(self):
        spec = self.spec
        for package in spec.packages:
            for pcomar in package.providesComar:
                comaruri = join(self.location,
                                ctx.const.comar_dir, pcomar.script)
                self.url.uri = comaruri
                self.fetch(ctx.const.comar_dir)

    def fetch_additionalFiles(self):
        spec = self.spec
        for pkg in spec.packages:
            for afile in pkg.additionalFiles:
                afileuri = join(self.location, 
                                ctx.const.files_dir, afile.filename)
                self.url.uri = afileuri
                self.fetch(ctx.const.files_dir)

    def fetch(self, appendDest=""):
        from fetcher import fetch_url

        ctx.ui.info(_("Fetching %s") % self.url.uri)
        dest = join(self.dest, appendDest)
        fetch_url(self.url, dest)


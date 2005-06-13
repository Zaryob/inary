# -*- coding: utf-8 -*-
# package bulding stuff
# maintainer: baris and meren

# python standard library
import os

from specfile import SpecFile
from fetcher import Fetcher
# from archive import Archive
# import pisipackage
import util
import config
import ui

class PisiBuildError(Exception):
    pass

# FIXME: this eventually has to go to ui module
def displayProgress(pd):
    out = '\r%-30.30s %3d%% %12.2f %s' % \
        (pd['filename'], pd['percent'], pd['rate'], pd['symbol'])
    ui.info(out)

class PisiBuild:
    """PisiBuild class, provides the package build and creation routines"""
    def __init__(self, pspecfile):
        self.pspecfile = pspecfile
        spec = SpecFile()
        spec.read(pspecfile)
        spec.verify()                  # check pspec integrity

        self.spec = spec

    def install(self):
        ui.info("Building PISI source package: %s\n" % self.spec.sourceName)
        ui.info("Fetching source from: %s" % self.spec.archiveUri)
        self.fetchArchive(displayProgress)
        ui.info("\n")
        ui.info("Source archive is stored: %s/%s\n" %(config.archives_dir(), self.archiveName))
        # unpackArchive()
        # applyPatches()
        # buildSource()
        # installTarget()
        self.buildPackages()

    def fetchArchive(self, percentHook=None):
        """fetch an archive and store to config.archives_dir() 
        using fether.Fetcher"""
        fetch = Fetcher(self.spec.archiveUri, self.spec.archiveName)

        # check if source already cached
        destpath = fetch.filedest + "/" + fetch.filename
        if os.access(destpath, os.R_OK):
            if util.md5_file(destpath)==self.spec.archiveMD5:
                ui.info(' [cached]')
                return

        if percentHook:
            fetch.percentHook = percentHook
        fetch.fetch()

    def unpackArchive(self):
	archive = Archive(self.spec.archiveType, self.spec.archiveName)
	archive.unpack()
        pass

    def applyPatches(self):
        pass

    def buildSource(self):
        pass

    def installTarget(self):
        pass

    def buildPackages(self):
        for package in self.spec.packages:
            ui.info("** Building package %s\n" % package.name);
    

# -*- coding: utf-8 -*-

# python standard library
import os
from os.path import basename

from specfile import SpecFile
from fetcher import Fetcher
# from archive import Archive
# import pisipackage
import util
import config


class PisiBuildError(Exception):
    pass

class PisiBuild:
    """PisiBuild class, provides the package build and creation routines"""
    def __init__(self, pspecfile):
        self.pspecfile = pspecfile
        spec = SpecFile()
        spec.read(pspecfile)
        spec.verify()                  # check pspec integrity

        # additional processing on spec file
        self.archiveName = basename(spec.archiveUri)
        self.spec = spec

    def fetchArchive(self, percentHook=None):
        """fetch an archive and store to pisi.config.archives_dir
        using fether.Fetcher"""
        fetch = Fetcher(self.spec.archiveUri)

        # check if source already cached
        destpath = fetch.filedest + "/" + fetch.filename
        if os.access(destpath, os.R_OK):
            if util.md5_file(destpath)==self.spec.archiveMD5:
                util.information(fetch.filename + " cached\n")
                return

        if percentHook:
            fetch.percentHook = percentHook
        fetch.fetch()

    def unpackArchive(self):
        pass

    def applyPatches(self):
        pass

    def buildSource(self):
        pass

    def installTarget(self):
        pass

    def buildPackages(self):
        for package in self.spec.packages:
            util.information("** Building package %s\n" % package.name);
    

# -*- coding: utf-8 -*-

# python standard library
from os.path import basename

from specfile import SpecFile
from fetcher import Fetcher
# import archive
# import pisipackage
# import pisiutils # patch, fileutils?
import pisiconfig

class PisiBuildError(Exception):
    pass

class PisiBuild:
    """PisiBuild class, provides the package build and creation rutines"""
    def __init__(self, pspecfile):
	self.pspecfile = pspecfile
	pspec = SpecFile()
        pspec.read(pspecfile)
        pspec.verify()                  # check pspec integrity

	self.packageName = pspec.sourceName

	self.archiveUri = pspec.archiveUri
	self.archiveName = basename(self.archiveUri)
	self.archiveType = pspec.archiveType
	self.archiveHash = pspec.archiveHash

	self.pspec = pspec

    def fetchArchive(self):
	fetch = Fetcher(self.archiveUri)
	fetch.fetch()

def usage(progname = "pisi-build"):
    print """
Usage:
%s [options] package-name.pspec
""" %(progname)

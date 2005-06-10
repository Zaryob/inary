# -*- coding: utf-8 -*-

# python standard library
from os.path import basename

from specfile import SpecFile
from fetcher import Fetcher
# from archive import Archive
# import pisipackage
# import pisiutils # patch, fileutils?
import pisiconfig

class PisiBuildError(Exception):
    pass

class PisiBuild:
    """PisiBuild class, provides the package build and creation rutines"""
    def __init__(self, pspecfile):
	self.pspecfile = pspecfile
	spec = SpecFile()
        spec.read(pspecfile)
        spec.verify()                  # check pspec integrity

        # additional processing on spec file
	self.archiveName = basename(spec.archiveUri)
        self.spec = spec

    def fetchArchive(self, percentHook=None):
	"""fetch an archive and store to pisiconfig.archives_dir
	using fether.Fetcher"""
	fetch = Fetcher(self.spec.archiveUri)
	if percentHook:
	    fetch.percentHook = percentHook
	fetch.fetch()

    def unpackArchive(self):
	pass

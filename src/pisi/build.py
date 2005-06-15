# -*- coding: utf-8 -*-
# package bulding stuff
# maintainer: baris and meren

# python standard library
import os

from specfile import SpecFile
from fetcher import Fetcher
from archive import Archive

# import pisipackage
import util
import config
import ui

class PisiBuildError(Exception):
    pass

# FIXME: this eventually has to go to ui module
# Infact all ui calls has nothing to do with this build process.
# There more of them in PisiBuild...
# And maybe we should consider moving PisiBuild.build() back to pisi-build CLI too.
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

    def build(self):
        ui.info("Building PISI source package: %s\n" % self.spec.source.name)
        ui.info("Fetching source from: %s\n" % self.spec.source.archiveUri)
        self.fetchArchive(displayProgress)
        ui.info("Source archive is stored: %s/%s\n"
                %(config.archives_dir(), self.spec.source.archiveName))
	
	self.solveBuildDependencies()
	
	ui.info("Unpacking archive...\n")
        self.unpackArchive()
        
	# applyPatches()

	self.actionScript = open( os.path.dirname( self.pspecfile ) + '/' + 'actions' ).read()

	os.chdir( config.build_work_dir( self.spec.source.name, self.spec.source.version, self.spec.source.release ) + "/" + self.spec.source.name + "-" + self.spec.source.version)
	locals = globals = {}
	exec compile( self.actionScript , "error", "exec" ) in locals,globals
	locals['src_setup']()
	locals['src_build']()
	locals['src_install']()

    def fetchArchive(self, percentHook=None):
        """fetch an archive and store to config.archives_dir() 
        using fether.Fetcher"""
        fetch = Fetcher(self.spec.source.archiveUri,
                        self.spec.source.archiveName)

        # check if source already cached
        destpath = fetch.filedest + "/" + fetch.filename
        if os.access(destpath, os.R_OK):
            if util.md5_file(destpath)==self.spec.source.archiveMD5:
                ui.info('%s [cached]\n' % self.spec.source.archiveName)
                return

        if percentHook:
            fetch.percentHook = percentHook
        
	fetch.fetch()

	# FIXME: What a ugly hack! We should really find a cleaner way for output.
	if percentHook:
	    ui.info('\n')

    def solveBuildDependencies(self):
    	pass

    def unpackArchive(self):
	type = self.spec.source.archiveType
	fileName = self.spec.source.archiveName
	targetDir = config.build_work_dir(self.spec.source.name,
					  self.spec.source.version,
					  self.spec.source.release)
	archive = Archive(type, fileName, targetDir)
	archive.unpack()

    def applyPatches(self):
        pass

    def buildSource(self):
        pass

    def installTarget(self):
        pass

    def buildPackages(self):
        for package in self.spec.packages:
            ui.info("** Building package %s\n" % package.name);
    

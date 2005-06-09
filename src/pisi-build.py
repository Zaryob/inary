#!/usr/bin/python
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
	pspec = SpecFile(pspecfile)
        pspec.read()

	self.packageName = pspec.getFirstChildText("Source/Name")

	archiveNode = pspec.getFirstNode("Source/Archive")
	self.archiveUri = pspec.getNodeText(archiveNode).strip()
	self.archiveName = basename(self.archiveUri)
	self.archiveType = pspec.getNodeAttribute(archiveNode, "archType")
	self.archiveHash = pspec.getNodeAttribute(archiveNode, "md5sum")
	
	self.pspec = pspec

    def fetchArchive(self):
	fetch = Fetcher(self.archiveUri)
	fetch.fetch()


def information(message):
    print message

def usage(progname = "pisi-build"):
    print """
Usage:
%s [options] package-name.pspec
""" %(progname)

def main():
    import sys
    import getopt
    
    # wrapper for usage(progname) function
    help = lambda: usage(sys.argv[0])

    # getopt magic
    try:
	opts, args = getopt.getopt(sys.argv[1:],"h",["help"])
    except getopt.GetoptError:
	help()
	sys.exit(1)

    for opt, arg in opts:
	if opt == "-h":
	    help()
	    sys.exit(1)

    # pspec(PISI Spec) to be used for package
    pspec = ""

    # TODO: We accept only one pspec file (at a time) currently,
    # but pisi-build may build many packages (pspecs given in order)
    # sequentially.
    if len(args) != 1:
	help()
	raise PisiBuildError, "pisi-build excepts one (and only one) pspec file currently"
    else:
	pspec = args[0]


    # doing the real job... vs. vs...
    pb = PisiBuild(pspec)
    information("Building PISI package for: %s" % pb.packageName)
    information("Fetching source from: %s (be patient)" % pb.archiveUri)
    print pb.archiveType, pb.archiveHash
    pb.fetchArchive()
    information("Source archive is stored: %s/%s" %(pisiconfig.archives_dir, pb.archiveName))
#     pb.unpackArchive()
#     pb.applyPatches()
#     pb.buildSource()
#     pb.installTarget()
#     pb.buildPisiPackage()
    

if __name__ == "__main__":
    main()

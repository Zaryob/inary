#!/usr/bin/python
# -*- coding: utf-8 -*-

from specfile import SpecFile
from fetcher import Fetcher
# import archive
# import pisipackage
# import pisiutils # patch, fileutils?

class PisiBuildError(Exception):
    pass

class PisiBuild:
    """PisiBuild class, provides the package build and creation rutines"""
    def __init__(self, pspecfile):
	self.pspecfile = pspecfile
	self.pspec = SpecFile(pspecfile)
	self.packagename = self.pspec.getFirstChildText("PSPEC/Source/Name")
	self.sourceuri = self.pspec.getFirstChildText("PSPEC/Source/Archive").strip()

    def fetchArchive(self):
	fetch = Fetcher(self.sourceuri)
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
    information("Building PISI package for: %s" % pb.packagename)
    information("Fetching source from: %s" % pb.sourceuri)
    pb.fetchArchive()
#     pb.unpackArchive()
#     pb.applyPatches()
#     pb.buildSource()
#     pb.installTarget()
#     pb.buildPisiPackage()
    

if __name__ == "__main__":
    main()

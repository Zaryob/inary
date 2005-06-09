# -*- coding: utf-8 -*-

# python standard library modules
import urlparse
import urllib, urllib2
import os
from sys import argv
from sys import exit

# pisi modules
import pisiconfig

class FetchError (Exception):
    pass


class ProgressMeter:
    def __init__ (self,):
    	pass
    

class Fetcher:
    """Yet another Pisi tool for fetching files from various sources.."""
    def __init__(self, uri):
        self.uri = uri
        self.filedest = pisiconfig.archives_dir
        self.scheme = "file"
        self.netloc = ""
        self.filepath = ""
        self.filename = ""

    def fetch (self):
        from string import split
        u = urlparse.urlparse(self.uri)
        self.scheme, self.netloc, self.filepath = u[0], u[1], u[2]
        self.filename = split(self.filepath, "/")[-1:][0]

        if self.filename == "":
            self.err("filename error")

        if os.access(self.filedest, os.W_OK) == False:
            self.err("no perm to write destination")

        scheme_err = lambda: self.err("unexpected scheme")

        actions = {
            'file': self.fetchLocalFile,
            'http': self.fetchRemoteFile,
            'ftp' : self.fetchRemoteFile
            }; actions.get(self.scheme, scheme_err)()

    def fetchLocalFile (self):
        from shutil import copyfile

        if os.access(self.filepath, os.F_OK) == False:
            self.err("no such file or no perm to read")

        copyfile(self.filepath, self.filedest + "/" + self.filename)

    def fetchRemoteFile (self):
    	from httplib import HTTPException

    	try:
    	    file = urllib2.urlopen(self.uri)
            headers = file.info()
	    
    	except ValueError, e:
            self.err('%s' % (e, ))
	except IOError, e:
            self.err('%s' % (e, ))
	except OSError, e:
            self.err('%s' % (e, ))
	except HTTPException, e:
	    self.err(('(%s): %s') % (e.__class__.__name__, e))

        if not headers is None and not headers.has_key('Content-Length'):
            self.err('file not found')
	else: totalsize = int(headers['Content-Length'])

        dest = open(self.filedest + "/" + self.filename , "w")

	bs = 1024*4
	size = 0
	oldpercent = -1
	#FIXME: güzel, flexible bir progress nesnesi hazırlamak lazım.
	#       şimdilik böyle kalsın, haftasonu hallederim..
	chunk = file.read(bs)
	size = size + len(chunk)
	while chunk:
	    dest.write(chunk)
	    chunk = file.read(bs)
	    size = size + len(chunk)
	    percent = (size * 100) / totalsize
	    if size != totalsize and oldpercent != percent:
	    	print "%%%d" % (percent)
		oldpercent = percent

        dest.close(); print "%100" 

    def err (self, error):
        raise FetchError(error)


def usage():
    print "Usage: %s URI" % argv[0]

def main():
    if len(argv) != 2:
        usage()
        exit(1)

    f = Fetcher(argv[1])
    f.fetch()

if __name__ == "__main__":
    main()

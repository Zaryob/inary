#!/usr/bin/python
# -*- coding: utf-8 -*-

import urlparse
import urllib
import os
from sys import argv
from sys import exit

class FetchError (Exception):
	pass

class Fetcher:
	"""Yet another Pisi tool for fetching files from various sources.."""
	def __init__(self, uri):
		self.uri = uri
		self.filedest = "/var/tmp/pisi/cache"
		self.builddir = "/var/tmp/pisi/work"
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

		scheme_err = lambda: self.err("unexpected scheme (expecting file, http or ftp)")

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
		try:
			file = urllib.urlopen(self.uri)

		except IOError, e:
			self.err(e.strerror[1])

		dest = open(self.filedest + "/" + self.filename , "w")
		dest.write(file.read())
	
	def err (self, error):
		raise FetchError, error
	
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

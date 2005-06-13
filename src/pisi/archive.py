# utilities to extract and build archives of zip, tar, targz, tarbz2
# maintainer: baris and meren

import tarfile
import zipfile

import config

class ArchiveBase(object):
    def __init__(self, filename, type):
	self.type = type
	self.filename = filename

class ArchiveTarFile(ArchiveBase):
    def __init__(self, filename, type):
	super(ArchiveTarFile, self).__init__(filename, type)

    def unpack(self):
	if self.type == "targz":
	    tar = tarfile.open(config.archives_dir()+"/"+self.filename, 'r:gz')
	    for tarinfo in tar:
		tar.extract(tarinfo)
	    tar.close()

class ArchiveZip(ArchiveBase):
    def __init__(self, filename, type):
	super(ArchiveZip, self).__init__(filename, type)

    def unpack(self):
	print "lolo"

class Archive:
    """Unpack magic for Archive files..."""

    def __init__(self, type, filename):
	"""accepted archive types:
	targz, tarbz2, zip, tar"""	
	
	actions = {
	    'targz': ArchiveTarFile,
	    'tarbz2': ArchiveTarFile,
	    'tar': ArchiveTarFile,
	    'zip': ArchiveZip
	    }
	
	self.archive = actions.get(type)(filename, type)

    def unpack(self):
	self.archive.unpack()

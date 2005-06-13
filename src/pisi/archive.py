# utilities to extract and build archives of zip, tar, targz, tarbz2
# maintainer: baris and meren

import tarfile

import config

class ArchiveTarFile:
    def __init__(self, filename, type):
	self.type = type
	self.filename = filename

    def unpack(self):
	if self.type == "targz":
	    tar = tarfile.open(config.archives_dir()+"/"+self.filename, 'r:gz')
	    for tarinfo in tar:
		tar.extract(tarinfo)
	    tar.close()

class ArchiveZip:
    pass


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

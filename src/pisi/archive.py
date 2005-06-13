# utilities to extract and build archives of zip, tar, targz, tarbz2
# maintainer: baris and meren

import config

class ArchiveTarGZ:
    def __init__(self, filename):
	print "testing...%s" %filename

    def unpack(self):
	print "unpack is cool"

class ArchiveTarBZ2:
    pass

class ArchiveZip:
    pass

class ArchiveTar:
    pass

class Archive:
    """Unpack magic for Archive files..."""

    def __init__(self, type, filename):
	"""accepted archive types:
	targz, tarbz2, zip, tar"""	
	
	actions = {
	    'targz': ArchiveTarGZ,
	    'tarbz2': ArchiveTarBZ2,
	    'zip': ArchiveZip,
	    'tar': ArchiveTar
	    }
	
	self.archive = actions.get(type)(filename)

    def unpack(self):
	self.archive.unpack()

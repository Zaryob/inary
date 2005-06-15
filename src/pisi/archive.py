# -*- coding: utf-8 -*-
# unpack magic
# maintainer baris and meren

#standart lisbrary modules
import os
import sys
import tarfile
import zipfile

#pisi modules
import config

class ArchiveBase(object):
    def __init__(self, type, fileName, targetDir):
	self.type = type
	self.fileName = fileName
	self.filePath = config.archives_dir() + '/' + self.fileName
	self.targetDir = targetDir

class ArchiveTarFile(ArchiveBase):
    def __init__(self, type, fileName, targetDir):
	super(ArchiveTarFile, self).__init__(type, fileName, targetDir)

    def unpack(self):
	if self.type == 'targz':
	    tar = tarfile.open(self.filePath, 'r:gz')
	    for tarinfo in tar:
		tar.extract(tarinfo)
	    tar.close()

class ArchiveZip(ArchiveBase):
    def __init__(self, type, fileName, targetDir):
	super(ArchiveZip, self).__init__(type, fileName, targetDir)

    def unpack(self):
        zip = zipfile.ZipFile(self.filePath, 'r')
        fileNames = zip.namelist()
        for file in fileNames:
            ofile = config.archives_dir() + '/' + file
	    print ofile
            if not os.path.exists(ofile):
                os.mkdir(ofile)
                continue
            elif os.path.exists(ofile):    #maybe ofile is not a dir, but file.
                continue                   #so we have to check..
            buff = open (ofile, 'wb')
            fileContent = zip.read(file)
            buff.write(fileContent)
            buff.close()
        zip.close()
                
class Archive:
    """Unpack magic for Archive files..."""

    def __init__(self, type, fileName, targetDir):
	"""accepted archive types:
	targz, tarbz2, zip, tar"""	
	
	actions = {
	    'targz': ArchiveTarFile,
	    'tarbz2': ArchiveTarFile,
	    'tar': ArchiveTarFile,
	    'zip': ArchiveZip
	    }
	
	self.archive = actions.get(type)(type, fileName, targetDir)

    def unpack(self):
	self.archive.unpack()

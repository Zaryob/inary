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
import util

class ArchiveBase(object):
    def __init__(self, type, fileName):
	self.type = type
	self.fileName = fileName
	self.filePath = config.archives_dir() + '/' + self.fileName

    def unpack(self, targetDir):
	self.targetDir = targetDir
	# first we check if we need to clean-up our working env.
        if os.path.exists(self.targetDir):
	    util.purge_dir(self.targetDir)
	else:
	    os.makedirs(self.targetDir)

class ArchiveTarFile(ArchiveBase):
    def __init__(self, type, fileName):
	super(ArchiveTarFile, self).__init__(type, fileName)

    def unpack(self, targetDir):
	super(ArchiveTarFile, self).unpack(targetDir)

        rmode = ""
	if self.type == 'tar':
	    rmode = 'r:'
	elif self.type == 'targz':
	    rmode = 'r:gz'
	elif self.type == 'tarbz2':
	    rmode = 'r:bz2'
	tar = tarfile.open(self.filePath, rmode)
        oldwd = os.getcwd()
        os.chdir(self.targetDir)
	for tarinfo in tar:
	    tar.extract(tarinfo)
        os.chdir(oldwd)
	tar.close()

class ArchiveZip(ArchiveBase):
    def __init__(self, type, fileName):
	super(ArchiveZip, self).__init__(type, fileName)

    def unpack(self, targetDir):
	super(ArchiveZip, self).unpack(targetDir)

        zip = zipfile.ZipFile(self.filePath, 'r')
        for file in zip.namelist():
            ofile = self.targetDir + '/' + file

	    # a directory is present. lets continue
	    if os.path.isdir(ofile):
		continue
	    # do we need to create parent directory for our file?
            if not os.path.exists(os.path.dirname(ofile)):
                os.mkdir(ofile)
                continue
            info = zip.getinfo(file)
	    if hex(info.external_attr)[2] == 'A':
                target = zip.read(file)
		os.symlink(target, ofile)
            else:
                buff = open (ofile, 'wb')
                fileContent = zip.read(file)
                buff.write(fileContent)
                buff.close()

        zip.close()
                
class Archive:
    """Unpack magic for Archive files..."""

    def __init__(self, type, fileName):
	"""accepted archive types:
	targz, tarbz2, zip, tar"""	
	
	actions = {
	    'targz': ArchiveTarFile,
	    'tarbz2': ArchiveTarFile,
	    'tar': ArchiveTarFile,
	    'zip': ArchiveZip
	    }
	
	self.archive = actions.get(type)(type, fileName)

    def unpack(self, targetDir):
	self.archive.unpack(targetDir)

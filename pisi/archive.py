# -*- coding: utf-8 -*-
# unpack magic
# maintainer baris and meren

#standart lisbrary modules
import os
import sys
import tarfile
import zipfile
from context import ctx

#pisi modules
import util

class ArchiveError:
    pass

class ArchiveBase(object):
    def __init__(self, filepath, atype):
	self.filePath = filepath
	self.type = atype

    def unpack(self, targetDir):
	self.targetDir = targetDir
	# first we check if we need to clean-up our working env.
        if os.path.exists(self.targetDir):
	    util.clean_dir(self.targetDir)
	else:
	    os.makedirs(self.targetDir)

class ArchiveTarFile(ArchiveBase):
    def __init__(self, filepath, type="tar"):
	super(ArchiveTarFile, self).__init__(filepath, type)

    def unpack(self, targetDir):
	super(ArchiveTarFile, self).unpack(targetDir)

        rmode = ""
	if self.type == 'tar':
	    rmode = 'r:'
	elif self.type == 'targz':
	    rmode = 'r:gz'
	elif self.type == 'tarbz2':
	    rmode = 'r:bz2'
        else:
            raise ArchiveError("Archive type not recognized")

	tar = tarfile.open(self.filePath, rmode)
        oldwd = os.getcwd()
        os.chdir(self.targetDir)
	for tarinfo in tar:
	    tar.extract(tarinfo)
        os.chdir(oldwd)
	tar.close()

class ArchiveZip(ArchiveBase):
    def __init__(self, filepath, type="zip"):
	super(ArchiveZip, self).__init__(filepath, type)

    def unpack_file_cond(self, pred, targetDir, archiveRoot=''):
        """ unpack file according to predicate function filename -> bool"""
	super(ArchiveTarFile, self).unpack(targetDir)

        zip = zipfile.ZipFile(self.filePath, 'r')
        for file in zip.namelist():
            if pred(file):              # check if condition holds
                if archiveRoot!='':
                    # change archiveRoot
                    if util.subpath(archiveRoot, file):
                        file = util.removepathprefix(archiveRoot, file)
                    else:
                        continue        # don't extract if not under
                ofile = os.path.join(targetDir, file)
                if os.path.isdir(ofile):
                    continue
                util.check_dir(os.path.dirname(ofile))
                if hex(info.external_attr)[2] == 'A':
                    target = zip.read(file)
                    os.symlink(target, ofile)
                else:
                    buff = open (ofile, 'wb')
                    fileContent = zip.read(file)
                    buff.write(fileContent)
                    buff.close()
        zip.close()

    def unpack_file(self, path, targetDir):
        unpack_file(self, lambda f:f==path, targetDir)

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
	    # O.K. we know following line is dull. What we wanted to
	    # do was to compare the equality to 0xa0000000. But there
	    # is a known problem in Python regarding the hex/oct
	    # constants. Please see Guido's explanation at
	    # http://mail.python.org/pipermail/python-dev/2003-February/033029.html
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

    def __init__(self, filepath, type):
	"""accepted archive types:
	targz, tarbz2, zip, tar"""	
	
	handlers = {
	    'targz': ArchiveTarFile,
	    'tarbz2': ArchiveTarFile,
	    'tar': ArchiveTarFile,
	    'zip': ArchiveZip
	    }
	
	self.archive = handlers.get(type)(filepath, type)

    def unpack(self, targetDir):
	self.archive.unpack(targetDir)

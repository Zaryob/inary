# -*- coding: utf-8 -*-
# Archive module provides access to regular archive file types.
# maintainer baris and meren

#standard lisbrary modules
import os
import sys
import tarfile
import zipfile
from config import config

#pisi modules
import util

class ArchiveError:
    pass

class ArchiveBase(object):
    """Base class for Archive classes."""
    def __init__(self, filepath, atype):
        self.filePath = filepath
        self.type = atype

    def unpack(self, targetDir, cleanDir = False):
        self.targetDir = targetDir
        # first we check if we need to clean-up our working env.
        if os.path.exists(self.targetDir):
            if cleanDir:
                util.clean_dir(self.targetDir)
        else:
            os.makedirs(self.targetDir)

class ArchiveTar(ArchiveBase):
    """ArchiveTar handles tar archives depending on the compression
    type. Provides access to tar, tar.gz and tar.bz2 files. 

    This class provides the unpack magic for tar archives."""
    def __init__(self, filepath, type = "tar"):
        super(ArchiveTar, self).__init__(filepath, type)

    def unpack(self, targetDir, cleanDir = False):
        """Unpack tar archive to a given target directory(targetDir)."""
        super(ArchiveTar, self).unpack(targetDir, cleanDir)

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
    """ArchiveZip handles zip archives. 

    Being a zip archive PISI packages also use this class
    extensively. This class provides unpacking and packing magic for
    zip archives."""
    
    symmagic = 2716663808 #long of hex val '0xA1ED0000L'
    
    def __init__(self, filepath, type = "zip", mode = 'r'):
        super(ArchiveZip, self).__init__(filepath, type)

        self.zip = zipfile.ZipFile(self.filePath, mode)

    def close(self):
        """Close the zip archive."""
        self.zip.close()

    def add_to_archive(self, fileName):
        """Add file or directory path to the zip file"""
        # It's a pity that zipfile can't handle unicode strings. Grrr!
        fileName = str(fileName)
        if os.path.isdir(fileName) and not os.path.islink(fileName):
            self.zip.writestr(os.path.join(fileName, ''))
            for f in os.listdir(fileName):
               self.add_to_archive(os.path.join(fileName, f))
        else:
            if os.path.islink(fileName):
                dest = os.readlink(fileName)
                attr = zipfile.ZipInfo()
                attr.filename = fileName
                attr.create_system = 3
                attr.external_attr = self.symmagic 
                self.zip.writestr(attr, dest)
            else:
                self.zip.write(fileName, fileName, zipfile.ZIP_DEFLATED)

    def add_basename_to_archive(self, fileName):
        """Add only the basepath to the zip file. For example; if the given
        fileName parameter is /usr/local/bin/somedir, this function
        will create only the base directory/file somedir in the
        archive."""
        cwd = os.getcwd()
        pathName = os.path.dirname(fileName)
        fileName = os.path.basename(fileName)
        if pathName:
            os.chdir(pathName)
        self.add_file(fileName)
        os.chdir(cwd)

    def unpack_file_cond(self, pred, targetDir, archiveRoot = ''):
        """Unpack/Extract a file according to predicate function filename ->
        bool"""
        zip = self.zip
        for info in zip.infolist():
            if pred(info.filename):   # check if condition holds

                # below code removes that, so we find it here
                isdir = info.filename.endswith('/')
                
                # calculate output file name
                if archiveRoot=='':
                    outpath = info.filename
                else:
                    # change archiveRoot
                    if util.subpath(archiveRoot, info.filename):
                        outpath = util.removepathprefix(archiveRoot,
                                                        info.filename)
                    else:
                        continue        # don't extract if not under

                ofile = os.path.join(targetDir, outpath)

                if isdir:               # a directory is present.
                    continue            # FIXME: do nothing!

                # check that output dir is present
                util.check_dir(os.path.dirname(ofile))

                if info.external_attr == self.symmagic:
                    target = zip.read(info.filename)
                    os.symlink(target, ofile)
                else:
                    perm = info.external_attr
                    perm &= 0x00FF0000
                    perm >>= 16
                    perm |= 0x00000100
                    buff = open (ofile, 'wb')
                    fileContent = zip.read(info.filename)
                    buff.write(fileContent)
                    buff.close()
                    os.chmod(ofile, perm)

    def unpack_files(self, paths, targetDir):
        self.unpack_file_cond(lambda f:f in paths, targetDir)

    def unpack_dir(self, path, targetDir):
        self.unpack_file_cond(lambda f:util.subpath(path,f), targetDir)

    def unpack_dir_flat(self, path, targetDir):
        self.unpack_file_cond(lambda f:util.subpath(path,f), targetDir, path)

    def unpack(self, targetDir, cleanDir=False):
        super(ArchiveZip, self).unpack(targetDir, cleanDir)

        self.unpack_file_cond(lambda f: True, targetDir)
        self.close()
        return 

class Archive:
    """Archive is the main factory for ArchiveClasses, regarding the
    Abstract Factory Pattern :)."""

    def __init__(self, filepath, type):
        """accepted archive types:
        targz, tarbz2, zip, tar"""

        handlers = {
            'targz': ArchiveTar, 
            'tarbz2': ArchiveTar,
            'tar': ArchiveTar,
            'zip': ArchiveZip
        }

        self.archive = handlers.get(type)(filepath, type)

    def unpack(self, targetDir, cleanDir = False):
        self.archive.unpack(targetDir, cleanDir)

    def unpack_files(self, files, targetDir):
        self.archive.unpack_files(files, targetDir)

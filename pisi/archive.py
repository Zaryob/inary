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

    def unpack(self, targetDir, cleanDir=False):
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
    def __init__(self, filepath, type="tar"):
        super(ArchiveTar, self).__init__(filepath, type)

    def unpack(self, targetDir):
        """Unpack tar archive to a given target directory(targetDir)."""
        super(ArchiveTar, self).unpack(targetDir)

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
    
    def __init__(self, filepath, type="zip", mode='r'):
        super(ArchiveZip, self).__init__(filepath, type)
        self.zip = zipfile.ZipFile(filepath, mode)

    def close(self):
        """Close the zip archive."""
        self.zip.close()

    def add_to_archive(self, fileName):
        """A wrapper function to handle working directory sh*t"""

        # Fuck zipfile! It's a pity that it can't handle unicode strings. Grrr!
        fileName = str(fileName)
        cwd = os.getcwd()
        pathName = os.path.dirname(fileName)
        fileName = os.path.basename(fileName)
        os.chdir(pathName)
        self.add_file(fileName)
        os.chdir(cwd)

    def add_file(self, fileName):
        """Add file or directory to a zip file"""
        if os.path.isdir(fileName) and not os.path.islink(fileName):
            self.zip.writestr(fileName + '/', '')
            for f in os.listdir(fileName):
               self.add_file(fileName + '/' + f)
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

    def unpack_file_cond(self, pred, targetDir, archiveRoot=''):
        """Unpack/Extract a file according to predicate function filename ->
        bool"""
        super(ArchiveZip, self).unpack(targetDir, False)
        zip = self.zip
        for fileName in zip.namelist():
            if pred(fileName):   # check if condition holds

                # calculate output file name
                if archiveRoot!='':
                    # change archiveRoot
                    if util.subpath(archiveRoot, fileName):
                        print '!', archiveRoot, fileName
                        fileName = util.removepathprefix(archiveRoot, fileName)
                        print '*', fileName
                    else:
                        
                        continue        # don't extract if not under
                ofile = os.path.join(targetDir, fileName)
                print 'ofile ', ofile

                # a directory is present. lets continue
                if fileName.endswith('/'):
                    continue

                # check that output dir is present
                util.check_dir(os.path.dirname(ofile))

                info = zip.getinfo(fileName)

                if info.external_attr == self.symmagic:
                    target = zip.read(fileName)
                    os.symlink(target, ofile)
                else:
                    inf = zip.getinfo(fileName)
                    perm = inf.external_attr
                    perm &= 0x00FF0000
                    perm >>= 16
                    perm |= 0x00000100
                    buff = open (ofile, 'wb')
                    fileContent = zip.read(fileName)
                    buff.write(fileContent)
                    buff.close()
                    os.chmod(ofile, perm)

    def unpack_files(self, paths, targetDir):
        self.unpack_file_cond(lambda f:f in paths, targetDir)

    def unpack_dir(self, path, targetDir):
        self.unpack_file_cond(lambda f:util.subpath(path,f), targetDir)

    def unpack_dir_flat(self, path, targetDir):
        self.unpack_file_cond(lambda f:util.subpath(path,f), targetDir, path)

    def unpack(self, targetDir):
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

    def unpack(self, targetDir):
        self.archive.unpack(targetDir)

    def unpack_files(self, files, targetDir):
        self.archive.unpack_files(files, targetDir)

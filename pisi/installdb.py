# -*- coding: utf-8 -*-
# installation database
# Author:  Eray Ozkural <eray@uludag.org.tr>


import os, fcntl
import bsddb.dbshelve as shelve

from config import config
from files import Files
import util

class InstallDBError(Exception):
    pass

class InstallDB:

    def __init__(self):
        util.check_dir(config.db_dir())
        self.db_filename = os.path.join(config.db_dir(), 'install.bdb')
        self.d = shelve.open(self.db_filename)
        self.files_dir = os.path.join(config.db_dir(), 'files')
        self.fdummy = open(self.db_filename)
        fcntl.flock(self.fdummy, fcntl.LOCK_EX)

    def __del__(self):
        #fcntl.flock(self.fdummy, fcntl.LOCK_UN)
        self.fdummy.close()
        
    def files_name(self, pkg, version, release):
        fn = pkg + '-' + version + '-' + release + '.xml'
        return os.path.join(self.files_dir, fn)

    def files(self, pkg):
        pkg = str(pkg)
        (status, version, release) = self.d[pkg]
        files = Files()
        files.read(self.files_name(pkg,version,release))
        return files

    def is_recorded(self, pkg):
        pkg = str(pkg)
        return self.d.has_key(pkg)

    def is_installed(self, pkg):
        pkg = str(pkg)
        if self.is_recorded(pkg):
            (status, version, release) = self.d[pkg]
            return status=='i'
        else:
            return False

    def get_version(self, pkg):
        pkg = str(pkg)
        (status, version, release) = self.d[pkg]
        return (version, release)

    def is_removed(self, pkg):
        pkg = str(pkg)
        if self.is_recorded(pkg):
            (status, version, release) = self.d[pkg]
            return status=='r'
        else:
            return False

    def install(self, pkg, version, release, files_xml):
        """install package with specific version and release"""
        pkg = str(pkg)
        if self.is_installed(pkg):
            raise InstallDBError("already installed")
        self.d[pkg] = ('i', version, release)
        util.copy_file(files_xml, self.files_name(pkg, version, release))

    def remove(self, pkg):
        pkg = str(pkg)
        (status, version, release) = self.d[pkg]
        self.d[pkg] = ('r', version, release)

    def purge(self, pkg):
        pkg = str(pkg)
        if self.d.has_key(pkg):
            (status, version, release) = self.d[pkg]
            f = self.files_name(pkg, version, release)
            if util.check_file(f):
                os.unlink(f)
            del self.d[pkg]

installdb = InstallDB()


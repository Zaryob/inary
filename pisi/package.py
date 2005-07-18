# -*- coding: utf-8 -*-

# package abstraction
# provides methods to add/remove files, extract control files
# maintainer: baris and meren

from os.path import join

import archive
from constants import const
from config import config
from purl import PUrl
from metadata import MetaData
from files import Files

class PackageError:
    pass

class Package:
    """PISI Package Class provides access to a pisi package (.pisi
    file)."""
    def __init__(self, packagefn, mode='r'):
        self.filepath = packagefn
        url = PUrl(packagefn)

        if url.isRemoteFile():
            from fetcher import fetchUrl
            from ui import ui
            dest = config.packages_dir()
            fetchUrl(url, dest, ui.Progress)
            self.filepath = join(dest, url.filename())

        self.impl = archive.ArchiveZip(self.filepath, 'zip', mode)

    def add_to_package(self, fn):
        """Add a file or directory to package"""
        self.impl.add_to_archive(fn)

    def close(self):
        """Close the package archive"""
        self.impl.close()

    def extract(self, outdir):
        """Extract entire package contents to directory"""
        self.extract_dir('', outdir)         # means package root

    def extract_files(self, paths, outdir):
        """Extract paths to outdir"""
        self.impl.unpack_files(paths, outdir)

    def extract_file(self, path, outdir):
        """Extract file with path to outdir"""
        self.extract_files([path], outdir)

    def extract_dir(self, dir, outdir):
        """Extract directory recursively, this function
        copies the directory archiveroot/dir to outdir"""
        self.impl.unpack_dir(dir, outdir)

    def extract_dir_flat(self, dir, outdir):
        """Extract directory recursively, this function
        unpacks the *contents* of directory archiveroot/dir inside outdir
        this is the function used by the installer"""
        self.impl.unpack_dir_flat(dir, outdir)
        
    def extract_PISI_files(self, outdir):
        """Extract PISI control files: metadata.xml, files.xml,
        action scripts, etc."""
        self.extract_files([const.metadata_xml, const.files_xml], outdir)
        self.extract_dir('config', outdir)

    def read(self, outdir = None):
        if not outdir:
            outdir = config.tmp_dir()

        # extract control files
        self.extract_PISI_files(outdir)

        self.metadata = MetaData()
        self.metadata.read( join(outdir, const.metadata_xml) )
        if not self.metadata.verify():
            raise PackageError("MetaData format wrong")

        self.files = Files()
        self.files.read( join(outdir, const.files_xml) )
        
    def pkg_dir(self):
        packageDir = self.metadata.package.name + '-' \
                     + self.metadata.package.version + '-' \
                     + self.metadata.package.release

        return join( config.lib_dir(), packageDir)

# bu fonksiyonun aynısı yukarıda başka bir isim ile var, biri fazla...
#     def pkg_dir_aux():
#         packageDir = self.metadata.package.name + '-' \
#                      + self.metadata.package.version + '-' \
#                      + self.metadata.package.release

#         return join( config.lib_dir(), packageDir)

    def comar_dir(self):
        return self.pkg_dir() + const.comar_dir_suffix

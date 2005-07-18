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
        self.filename = packagefn
        url = PUrl(packagefn)

        if url.isRemoteFile():
            from os import getcwd
            from fetcher import fetchUrl
            from ui import ui
            # TODO: belki Constants.packages_dir() gibi bir yere
            # indirmek daha iyi olur.
            fetchUrl(url, getcwd(), ui.Progress)
            self.filename = url.filename()

        self.impl = archive.ArchiveZip(self.filename, 'zip', mode)

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

    def read_info(self, outdir = None):
        if not outdir:
            outdir = config.tmp_dir()

        # extract control files
        self.package.extract_PISI_files(tmpdir)

        self.metadata = MetaData()
        self.metadata.read( join(tmpdir, config.metadata_xml) )
        if not metadata.verify():
            raise PackageError("MetaData format wrong")

        self.files = Files()
        self.files.read( join(tmpdir, const.files_xml) )
        
    def pkg_dir(self):
        packageDir = self.metadata.package.name + '-' \
                     + self.metadata.package.version + '-' \
                     + self.metadata.package.release

        return join( config.lib_dir(), packageDir)

    def comar_dir(self):
        return join( self.pkg_dir(), const.comar_dir_suffix)

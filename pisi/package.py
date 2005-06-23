# package abstraction
# provides methods to add/remove files, extract control files
# maintainer: baris and meren

import archive
from constants import constants
from config import config

class Package:
    """Package: PISI package class"""
    def __init__(self, packagefn, mode='r'):
        self.impl = archive.ArchiveZip(packagefn, 'zip', mode)
        self.filename = packagefn

    def add_file(self, fn):
        """add a file or directory to package"""
        self.impl.add_file(fn)

    def close(self):
        self.impl.close()

    def extract(self, outdir):
        """extract entire package contents to directory"""
        extract_dir('', outdir)         # means package root

    def extract_files(self, paths, outdir):
        """extract file with path to outdir"""
        impl.unpack_files(paths, outdir)

    def extract_dir(self, dir, outdir):
        """extract directory recursively, this function
        copies the directory archiveroot/dir to outdir"""
        impl.unpack_dir(path, outdir)

    def extract_dir_flat(self, dir, outdir):
        """extract directory recursively, this function
        unpacks the *contents* of directory archiveroot/dir inside outdir
        this is the function used by the installer"""
        impl.unpack_dir_flat(dir, outdir)
        
    def extract_PISI_files(self, outdir):
        """extract PISI control files: metadata.xml, files.xml,
        action scripts, etc."""
        self.extract_files([constants.metadata_xml, constants.files_xml,'Config'], outdir)


# package abstraction
# provides methods to add/remove files, extract control files
# maintainer: baris and meren

import archive
from constants import const
from config import config

class Package:
    """PISI Package Class provides access to a pisi package (.pisi
    file)."""
    def __init__(self, packagefn, mode='r'):
        self.impl = archive.ArchiveZip(packagefn, 'zip', mode)
        self.filename = packagefn

    def add_to_package(self, fn):
        """Add a file or directory to package"""
        self.impl.add_to_archive(fn)

    def close(self):
        """Close the package archive"""
        self.impl.close()

    def extract(self, outdir):
        """Extract entire package contents to directory"""
        extract_dir('', outdir)         # means package root

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


# package abstraction
# provides methods to add/remove files, extract control files
# maintainer: baris and meren

class Package:
    """Package: PISI package class"""
    def __init__(self, packagefn, mode):
        self.filename = packagefn
        self.mode = mode
        # etc. etc.

    def add_file(fn):
        """add a file to package"""

    def extract(outdir):
        """extract package contents to directory"""

    def extract_PISI_files(outdir):
        """extract PISI control files: metadata.xml, files.xml,
        action scripts, etc."""

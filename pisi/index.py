# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# PISI source/package index

# Author:  Eray Ozkural <eray@uludag.org.tr>

import os

from pisi.package import Package
from pisi.xmlfile import XmlFile
import pisi.metadata as metadata
import pisi.packagedb as packagedb
from pisi.ui import ui
import pisi.util as util
from pisi.config import config
from pisi.constants import const
from pisi.purl import URI

class Index(XmlFile):

    def __init__(self):
        XmlFile.__init__(self,"PISI")
        self.sources = []
        self.packages = []

    def read(self, filename, repo = None):
        """Read PSPEC file"""

        self.filepath = filename
        url = URI(filename)
        if url.is_remote_file():
            from fetcher import fetchUrl

            dest = os.path.join(config.index_dir(), repo)
            if not os.path.exists(dest):
                os.makedirs(dest)
            fetchUrl(url, dest, ui.Progress)

            self.filepath = os.path.join(dest, url.filename())

        self.readxml(self.filepath)

        # find all binary packages
        packageElts = self.getAllNodes("Package")
        self.packages = [metadata.PackageInfo(p) for p in packageElts]
        
        self.unlink()
    
    def write(self, filename):
        """Write index file"""
        self.newDOM()
        for pkg in self.packages:
            self.addChild(pkg.elt(self))
        self.writexml(filename)
        self.unlink()
        
    def index(self, repo_uri):
        self.repo_dir = repo_uri
        for root, dirs, files in os.walk(repo_uri):
            for fn in files:
                if fn.endswith(const.package_prefix):
                    ui.info('Adding ' + fn + ' to package index\n')
                    self.add_package(os.path.join(root, fn), repo_uri)

    def update_db(self, repo):
        pkgdb = packagedb.get_db(repo)
        pkgdb.clear()
        for pkg in self.packages:
            pkgdb.add_package(pkg)

    def add_package(self, path, repo_uri):
        package = Package(path, 'r')
        # extract control files
        util.clean_dir(config.install_dir())
        package.extract_PISI_files(config.install_dir())

        md = metadata.MetaData()
        md.read(os.path.join(config.install_dir(), const.metadata_xml))
        if config.options and config.options.absolute_uris:
            md.package.packageURI = os.path.realpath(path)
        else:                           # create relative path by default
            # TODO: in the future we'll do all of this with purl/pfile/&helpers
            # After that, we'll remove the ugly repo_uri parameter from this
            # function.
            md.package.packageURI = util.removepathprefix(repo_uri, path)
        # check package semantics
        if md.has_errors():
            ui.error('Package ' + md.package.name + ': metadata corrupt\n')
        else:
            self.packages.append(md.package)

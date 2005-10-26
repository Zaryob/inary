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
# Author:  Eray Ozkural <eray@uludag.org.tr>


"""PISI source/package index"""


import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.metadata as metadata
import pisi.packagedb as packagedb
import pisi.util as util
from pisi.package import Package
from pisi.xmlfile import XmlFile
from pisi.uri import URI

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
            from fetcher import fetch_url

            dest = os.path.join(ctx.config.index_dir(), repo)
            if not os.path.exists(dest):
                os.makedirs(dest)
            fetch_url(url, dest, ctx.ui.Progress)

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
                if fn.endswith(ctx.const.package_suffix):
                    ctx.ui.info(_('Adding %s  to package index') %fn)
                    self.add_package(os.path.join(root, fn), repo_uri)

    def update_db(self, repo):
        pkgdb = packagedb.get_db(repo)
        pkgdb.clear()
        for pkg in self.packages:
            pkgdb.add_package(pkg)

    def add_package(self, path, repo_uri):
        package = Package(path, 'r')
        # extract control files
        util.clean_dir(ctx.config.install_dir())
        package.extract_PISI_files(ctx.config.install_dir())

        md = metadata.MetaData()
        md.read(os.path.join(ctx.config.install_dir(), ctx.const.metadata_xml))
        if ctx.config.options and ctx.config.options.absolute_uris:
            md.package.packageURI = os.path.realpath(path)
        else:                           # create relative path by default
            # TODO: in the future we'll do all of this with purl/pfile/&helpers
            # After that, we'll remove the ugly repo_uri parameter from this
            # function.
            md.package.packageURI = util.removepathprefix(repo_uri, path)
        # check package semantics
        if md.has_errors():
            ctx.ui.error(_('Package %s: metadata corrupt') % md.package.name)
        else:
            self.packages.append(md.package)

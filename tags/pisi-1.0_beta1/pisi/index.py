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

import pisi
import pisi.context as ctx
import pisi.specfile as specfile
import pisi.metadata as metadata
import pisi.packagedb as packagedb
import pisi.util as util
from pisi.package import Package
from pisi.pxml.xmlfile import XmlFile
import pisi.pxml.autoxml as autoxml
from pisi.uri import URI
import pisi.component as component
import pisi.specfile as specfile

class Error(pisi.Error):
    pass

class Index(XmlFile):
    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_Sources = [ [specfile.Source], autoxml.optional, "Source"]
    t_Packages = [ [metadata.Package], autoxml.optional, "Package"]
    t_Components = [ [component.Component], autoxml.optional, "Component"]

    def read_uri(self, filename, repo = None):
        """Read PSPEC file"""

        self.filepath = filename
        url = URI(filename)
        if url.is_remote_file():
            from fetcher import fetch_url
            assert repo
            dest = os.path.join(ctx.config.index_dir(), repo)
            if not os.path.exists(dest):
                os.makedirs(dest)
            fetch_url(url, dest, ctx.ui.Progress)

            self.filepath = os.path.join(dest, url.filename())

        self.read(self.filepath)

    def index(self, repo_uri):
        self.repo_dir = repo_uri
        for root, dirs, files in os.walk(repo_uri):
            for fn in files:
                if fn.endswith(ctx.const.package_suffix):
                    ctx.ui.info(_('Adding %s to package index') % fn)
                    self.add_package(os.path.join(root, fn), repo_uri)
                if fn == 'component.xml':
                    ctx.ui.info(_('Adding %s to component index') % fn)
                    self.add_component(os.path.join(root, fn))
                #if fn == 'pspec.xml':
                #    self.add_source(os.path.join(root, fn), repo_uri)

    def update_db(self, repo):
        pkgdb = packagedb.get_db(repo)
        pkgdb.clear()
        for comp in self.components:
            ctx.componentdb.update_component(comp)
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
        errs = md.errors()
        if md.errors():
            ctx.ui.error(_('Package %s: metadata corrupt') % md.package.name)
            ctx.ui.error(str(Error(*errs)))
        else:
            self.packages.append(md.package)

    def add_component(self, path):
        comp = component.Component()
        try:
            comp.read(path)
            self.components.append(comp)
        except:
            ctx.ui.error(_('Component in %s is corrupt') % path)
            #ctx.ui.error(str(Error(*errs)))

    def add_source(self, path):
        ctx.ui.info(_('Adding %s to source index') % fn)
        sf = specfile.SpecFile()
        sf.read(path)
        errs = sf.errors()
        if sf.errors():
            ctx.ui.error(_('SpecFile in %s is corrupt') % path)
            ctx.ui.error(str(Error(*errs)))
        else:
            self.sources.append(sf.source)

    #TODO: add source

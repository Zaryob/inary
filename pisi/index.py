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
import pisi.sourcedb as sourcedb
import pisi.util as util
from pisi.package import Package
from pisi.pxml.xmlfile import XmlFile
from pisi.file import File
import pisi.pxml.autoxml as autoxml
from pisi.uri import URI
import pisi.component as component
import pisi.specfile as specfile


class Error(pisi.Error):
    pass


class Index(XmlFile):
    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_Specs = [ [specfile.SpecFile], autoxml.optional, "SpecFile"]
    t_Packages = [ [metadata.Package], autoxml.optional, "Package"]
    t_Components = [ [component.Component], autoxml.optional, "Component"]

    def read_uri(self, filename, repo = None):
        """Read PSPEC file"""
        tmpdir = os.path.join(ctx.config.index_dir(), repo)
        self.read(filename, tmpDir=tmpdir, sha1sum=True, compress=File.xmill)

    def index(self, repo_uri, skip_sources=False):
        self.repo_dir = repo_uri
        for root, dirs, files in os.walk(repo_uri):
            for fn in files:
                if fn.endswith(ctx.const.package_suffix):
                    ctx.ui.info(_('Adding %s to package index') % fn)
                    self.add_package(os.path.join(root, fn), repo_uri)
                if fn == 'component.xml':
                    ctx.ui.info(_('Adding %s to component index') % fn)
                    self.add_component(os.path.join(root, fn))
                if fn == 'pspec.xml' and not skip_sources:
                    self.add_spec(os.path.join(root, fn), repo_uri)

    def update_db(self, repo, txn = None):
        for comp in self.components:
            ctx.componentdb.update_component(comp, txn=txn)
        ctx.packagedb.remove_repo(repo, txn=txn)
        for pkg in self.packages:
            ctx.packagedb.add_package(pkg, repo, txn=txn)
        ctx.sourcedb.remove_repo(repo, txn=txn)
        for sf in self.specs:
            ctx.sourcedb.add_spec(sf, repo, txn=txn)

    def add_package(self, path, repo_uri):
        package = Package(path, 'r')
        # extract control files
        util.clean_dir(ctx.config.install_dir())
        package.extract_PISI_files(ctx.config.install_dir())

        md = metadata.MetaData()
        md.read(os.path.join(ctx.config.install_dir(), ctx.const.metadata_xml))
        md.package.packageSize = os.path.getsize(path)
        if ctx.config.options and ctx.config.options.absolute_uris:
            # FIXME: the name "absolute_uris" does not seem to fit below :/
            md.package.packageURI = os.path.realpath(path)
        else:                           # create relative path by default
            # TODO: in the future well do all of this with purl/pfile/&helpers
            # really? heheh -- future exa
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

    def add_spec(self, path, repo_uri):
        ctx.ui.info(_('Adding %s to source index') % path)
        sf = specfile.SpecFile()
        sf.read(path)
        errs = sf.errors()
        if sf.errors():
            ctx.ui.error(_('SpecFile in %s is corrupt') % path)
            ctx.ui.error(str(Error(*errs)))
        else:
            if ctx.config.options and ctx.config.options.absolute_uris:
                sf.source.sourceURI = os.path.realpath(path)
            else:                           # create relative path by default
                sf.source.sourceURI = util.removepathprefix(repo_uri, path)
            self.specs.append(sf)


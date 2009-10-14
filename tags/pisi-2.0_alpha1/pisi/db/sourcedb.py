# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import re
import gzip
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import piksemel

import pisi
import pisi.specfile
import pisi.db.lazydb as lazydb

class SourceDB(lazydb.LazyDB):

    def init(self):

        self.__source_nodes = {}
        self.__pkgstosrc = {}

        repodb = pisi.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            self.__source_nodes[repo], self.__pkgstosrc[repo] = self.__generate_sources(doc)

        self.sdb = pisi.db.itembyrepo.ItemByRepo(self.__source_nodes, compressed=True)
        self.psdb = pisi.db.itembyrepo.ItemByRepo(self.__pkgstosrc)

    def __generate_sources(self, doc):

        sources = {}
        pkgstosrc = {}

        for spec in doc.tags("SpecFile"):
            src_name = spec.getTag("Source").getTagData("Name")
            sources[src_name] = gzip.zlib.compress(spec.toString())
            for package in spec.tags("Package"):
                pkgstosrc[package.getTagData("Name")] = src_name
        
        return sources, pkgstosrc

    def list_sources(self, repo=None):
        return self.sdb.get_item_keys(repo)

    def has_spec(self, name, repo=None):
        return self.sdb.has_item(name, repo)

    def get_spec(self, name, repo=None):
        spec, repo = self.get_spec_repo(name, repo)
        return spec

    def search_spec(self, terms, lang=None, repo=None):
        resum = '<Summary xml:lang="%s">.*?%s.*?</Summary>'
        redesc = '<Description xml:lang="%s">.*?%s.*?</Description>'
        if not lang:
            lang = pisi.pxml.autoxml.LocalText.get_lang()
        found = []
        for name, xml in self.sdb.get_items_iter(repo):
            if terms == filter(lambda term: re.compile(term, re.I).search(name) or \
                                            re.compile(resum % (lang, term), re.I).search(xml) or \
                                            re.compile(redesc % (lang, term), re.I).search(xml), terms):
                found.append(name)
        return found

    def get_spec_repo(self, name, repo=None):
        src, repo = self.sdb.get_item_repo(name, repo)
        spec = pisi.specfile.SpecFile()
        spec.parse(src)
        return spec, repo

    def pkgtosrc(self, name, repo=None):
        return self.psdb.get_item(name, repo)

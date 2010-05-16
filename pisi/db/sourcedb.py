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

import piksemel

import pisi
import pisi.specfile
import pisi.db.lazydb as lazydb

class SourceDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)

    def init(self):
        self.__source_nodes = {}
        self.__pkgstosrc = {}
        self.__revdeps = {}

        repodb = pisi.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            self.__source_nodes[repo], self.__pkgstosrc[repo] = self.__generate_sources(doc)
            self.__revdeps[repo] = self.__generate_revdeps(doc)

        self.sdb = pisi.db.itembyrepo.ItemByRepo(self.__source_nodes, compressed=True)
        self.psdb = pisi.db.itembyrepo.ItemByRepo(self.__pkgstosrc)
        self.rvdb = pisi.db.itembyrepo.ItemByRepo(self.__revdeps)

    def __generate_sources(self, doc):
        sources = {}
        pkgstosrc = {}

        for spec in doc.tags("SpecFile"):
            src_name = spec.getTag("Source").getTagData("Name")
            sources[src_name] = gzip.zlib.compress(spec.toString())
            for package in spec.tags("Package"):
                pkgstosrc[package.getTagData("Name")] = src_name
        
        return sources, pkgstosrc

    def __generate_revdeps(self, doc):
        revdeps = {}
        for spec in doc.tags("SpecFile"):
            name = spec.getTag("Source").getTagData("Name")
            deps = spec.getTag("Source").getTag("BuildDependencies")
            if deps:
                for dep in deps.tags("Dependency"):
                    revdeps.setdefault(dep.firstChild().data(), set()).add((name, dep.toString()))
        return revdeps

    def list_sources(self, repo=None):
        return self.sdb.get_item_keys(repo)

    def which_repo(self, name):
        return self.sdb.which_repo(self.pkgtosrc(name))

    def which_source_repo(self, name):
        source = self.pkgtosrc(name)
        return source, self.sdb.which_repo(source)

    def has_spec(self, name, repo=None):
        return self.sdb.has_item(name, repo)

    def get_spec(self, name, repo=None):
        spec, repo = self.get_spec_repo(name, repo)
        return spec

    def search_spec(self, terms, lang=None, repo=None, fields=None):
        """
        fields (dict) : looks for terms in the fields which are marked as True
        If the fields is equal to None this method will search in all fields

        example :
        if fields is equal to : {'name': True, 'summary': True, 'desc': False}
        This method will return only package that contents terms in the package
        name or summary
        """
        resum = '<Summary xml:lang=.(%s|en).>.*?%s.*?</Summary>'
        redesc = '<Description xml:lang=.(%s|en).>.*?%s.*?</Description>'
        if not fields:
            fields = {'name': True, 'summary': True, 'desc': True}
        if not lang:
            lang = pisi.pxml.autoxml.LocalText.get_lang()
        found = []
        for name, xml in self.sdb.get_items_iter(repo):
            if terms == filter(lambda term: (fields['name'] and \
                    re.compile(term, re.I).search(name)) or \
                    (fields['summary'] and \
                    re.compile(resum % (lang, term), re.I).search(xml)) or \
                    (fields['desc'] and \
                    re.compile(redesc % (lang, term), re.I).search(xml)), terms):
                found.append(name)
        return found

    def get_spec_repo(self, name, repo=None):
        src, repo = self.sdb.get_item_repo(name, repo)
        spec = pisi.specfile.SpecFile()
        spec.parse(src)
        return spec, repo

    def pkgtosrc(self, name, repo=None):
        return self.psdb.get_item(name, repo)

    def get_rev_deps(self, name, repo=None):
        try:
            rvdb = self.rvdb.get_item(name, repo)
        except Exception: #FIXME: what exception could we catch here, replace with that.
            return []

        rev_deps = []
        for pkg, dep in rvdb:
            node = piksemel.parseString(dep)
            dependency = pisi.dependency.Dependency()
            dependency.package = node.firstChild().data()
            if node.attributes():
                attr = node.attributes()[0]
                dependency.__dict__[attr] = node.getAttribute(attr)
            rev_deps.append((pkg, dependency))
        return rev_deps

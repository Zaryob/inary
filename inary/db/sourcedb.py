# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Standart Python Modules
import re
import gzip

# Inary Modules
import inary.analyzer
import inary.data.specfile as Specfile
import inary.db
import inary.db.lazydb as lazydb

# AutoXML Library
from inary.sxml import autoxml, xmlext

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class SourceDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)
        # self.init()

    def init(self):
        self.__source_nodes = {}
        self.__pkgstosrc = {}
        self.__revdeps = {}

        repodb = inary.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            self.__source_nodes[repo], self.__pkgstosrc[repo] = self.__generate_sources(
                doc)
            self.__revdeps[repo] = self.__generate_revdeps(doc)

        self.sdb = inary.db.itembyrepo.ItemByRepo(
            self.__source_nodes, compressed=True)
        self.psdb = inary.db.itembyrepo.ItemByRepo(self.__pkgstosrc)
        self.rvdb = inary.db.itembyrepo.ItemByRepo(self.__revdeps)

    @staticmethod
    def __generate_sources(doc):
        sources = {}
        pkgstosrc = {}

        for spec in xmlext.getTagByName(doc, "SpecFile"):
            src = xmlext.getNode(spec, "Source")
            src_name = xmlext.getNodeText(src, "Name")
            compressed_data = gzip.zlib.compress(
                xmlext.toString(spec).encode('utf-8'))
            sources[src_name] = compressed_data

            for package in xmlext.getTagByName(spec, "Package"):
                pkgstosrc[xmlext.getNodeText(package, "Name")] = src_name

        return sources, pkgstosrc

    @staticmethod
    def __generate_revdeps(doc):
        revdeps = {}

        for spec in xmlext.getTagByName(doc, "SpecFile"):
            src = xmlext.getNode(spec, "Source")
            name = xmlext.getNodeText(src, "Name")
            deps = xmlext.getNode(src, "BuildDependencies")
            if deps:
                for dep in xmlext.getTagByName(deps, "Dependency"):
                    revdeps.setdefault(
                        xmlext.getNodeText(dep), set()).add(
                        (name, xmlext.toString(dep)))

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

    def search_spec(self, terms, lang=None, repo=None, fields=None, cs=False):
        """
        fields (dict) : looks for terms in the fields which are marked as True
        If the fields is equal to None this method will search in all fields

        example :
        if fields is equal to : {'name': True, 'summary': True, 'desc': False}
        This method will return only package that contents terms in the package
        name or summary
        """
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not fields:
            fields = {'name': True, 'summary': True, 'desc': True}
        if not lang:
            lang = autoxml.LocalText.get_lang()
        found = []
        for name, xml in self.sdb.get_items_iter(repo):
            if terms == [term for term in terms if (fields['name'] and
                                                    re.compile(term, re.I).search(name)) or
                                                   (fields['summary'] and
                                                    re.compile(resum.format(lang, term), 0 if cs else re.I).search(
                                                        xml)) or
                                                   (fields['desc'] and
                                                    re.compile(redesc.format(lang, term), 0 if cs else re.I).search(
                                                        xml))]:
                found.append(name)
        return found

    def get_spec_repo(self, name, repo=None):
        src, repo = self.sdb.get_item_repo(name, repo)
        spec = Specfile.SpecFile()
        spec.parse(src)
        return spec, repo

    def pkgtosrc(self, name, repo=None):
        return self.psdb.get_item(name, repo)

    def get_rev_deps(self, name, repo=None):
        try:
            rvdb = self.rvdb.get_item(name, repo)
        except Exception:  # FIXME: what exception could we catch here, replace with that.
            return []

        rev_deps = []

        for pkg, dep in rvdb:
            node = xmlext.parseString(dep)
            dependency = inary.analyzer.dependency.Dependency()
            dependency.package = xmlext.getNodeText(node)

            if xmlext.getAttributeList(node):
                if xmlext.getNodeAttribute(node, "version"):
                    dependency.__dict__[
                        "version"] = xmlext.getNodeAttribute(node, "version")
                elif xmlext.getNodeAttribute(node, "release"):
                    dependency.__dict__[
                        "release"] = xmlext.getNodeAttribute(node, "release")
                else:
                    pass  # FIXME: ugly
            rev_deps.append((pkg, dependency))

        return rev_deps

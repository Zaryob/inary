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
import time
import gzip
import datetime

# Inary Modules
import inary.db
import inary.data.metadata
import inary.db.itembyrepo
import inary.db.lazydb as lazydb
import inary.analyzer.dependency

# AutoXML Library
from inary.sxml import xmlext

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class PackageDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)
        # self.init()

    def init(self):
        self.__package_nodes = {}  # Packages
        self.__revdeps = {}  # Reverse dependencies
        self.__obsoletes = {}  # Obsoletes
        self.__replaces = {}  # Replaces

        repodb = inary.db.repodb.RepoDB()
        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            self.__package_nodes[repo] = self.__generate_packages(doc)
            self.__revdeps[repo] = self.__generate_revdeps(doc)
            self.__obsoletes[repo] = self.__generate_obsoletes(doc)
            self.__replaces[repo] = self.__generate_replaces(doc)
        self.pdb = inary.db.itembyrepo.ItemByRepo(
            self.__package_nodes, compressed=True)
        self.rvdb = inary.db.itembyrepo.ItemByRepo(self.__revdeps)
        self.odb = inary.db.itembyrepo.ItemByRepo(self.__obsoletes)
        self.rpdb = inary.db.itembyrepo.ItemByRepo(self.__replaces)

    # Generate functions look sooo ugly
    @staticmethod
    def __generate_replaces(doc):
        replaces = []
        packages = xmlext.getTagByName(doc, "Package")
        for node in packages:
            if xmlext.getNodeText(node, "Replaces"):
                replaces.append(xmlext.getNodeText(node, "Name"))
        return replaces

    @staticmethod
    def __generate_obsoletes(doc):
        distribution = xmlext.getNode(doc, "Distribution")
        obsoletes = distribution and xmlext.getNode(distribution, "Obsoletes")
        src_repo = xmlext.getNode(doc, "SpecFile") is not None

        if not obsoletes or src_repo:
            return []
        return [xmlext.getNodeText(x)
                for x in xmlext.getTagByName(obsoletes, "Package")]

    @staticmethod
    def __generate_packages(doc):
        pdict = {}

        for x in xmlext.getTagByName(doc, "Package"):
            name = xmlext.getNodeText(x, "Name")
            compressed_data = gzip.zlib.compress(
                xmlext.toString(x).encode('utf-8'))
            pdict[name] = compressed_data

        return pdict

    @staticmethod
    def __generate_revdeps(doc):
        revdeps = {}
        for node in xmlext.getTagByName(doc, "Package"):
            name = xmlext.getNodeText(node, 'Name')
            deps = xmlext.getNode(node, 'RuntimeDependencies')
            if deps:
                for dep in xmlext.getTagByName(deps, "Dependency"):
                    revdeps.setdefault(
                        xmlext.getNodeText(dep), set()).add(
                        (name, xmlext.toString(dep)))

        return revdeps

    def has_package(self, name, repo=None):
        return self.pdb.has_item(name, repo)

    def get_package(self, name, repo=None):
        pkg, repo = self.get_package_repo(name, repo)
        return pkg

    def search_in_packages(self, packages, terms, lang=None):
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not lang:
            lang = inary.sxml.autoxml.LocalText.get_lang()
        found = []
        for name in packages:
            xml = self.pdb.get_item(name)
            if terms == [term for term in terms if re.compile(term, re.I).search(name) or
                         re.compile(resum.format(lang, term), re.I).search(xml) or
                         re.compile(redesc.format(lang, term), re.I).search(xml)]:
                found.append(name)
        return found

    def search_package(self, terms, lang=None,
                       repo=None, fields=None, cs=False):
        """
        fields (dict) : looks for terms in the fields which are marked as True
        If the fields is equal to None the method will search on all fields

        example :
        if fields is equal to : {'name': True, 'summary': True, 'desc': False}
        This method will return only package that contents terms in the package
        name or summary
        """
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not lang:
            lang = inary.sxml.autoxml.LocalText.get_lang()
        if not fields:
            fields = {'name': True, 'summary': True, 'desc': True}
        found = []
        for name, xml in self.pdb.get_items_iter(repo):
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

    @staticmethod
    def __get_version(meta_doc):
        history = xmlext.getNode(meta_doc, 'History')
        update = xmlext.getNode(history, 'Update')

        version = xmlext.getNodeText(update, 'Version')
        release = xmlext.getNodeAttribute(update, 'release')

        return version, release, None

    @staticmethod
    def __get_release(meta_doc):
        history = xmlext.getNode(meta_doc, 'History')
        update = xmlext.getNode(history, 'Update')

        release = xmlext.getNodeAttribute(update, 'release')

        return release

    @staticmethod
    def __get_last_date(meta_doc):
        history = xmlext.getNode(meta_doc, 'History')
        update = xmlext.getNode(history, 'Update')

        date = xmlext.getNodeText(update, 'Date')

        return date

    @staticmethod
    def __get_summary(meta_doc):
        summary = xmlext.getNodeText(meta_doc, 'Summary')

        return summary

    @staticmethod
    def __get_distro_release(meta_doc):
        distro = xmlext.getNodeText(meta_doc, 'Distribution')
        release = xmlext.getNodeText(meta_doc, 'DistributionRelease')

        return distro, release

    def get_version_and_distro_release(self, name, repo=None):
        if not self.has_package(name, repo):
            raise Exception(_('Package \"{}\" not found.').format(name))

        pkg_doc = xmlext.parseString(self.pdb.get_item(name, repo))

        return self.__get_version(pkg_doc) + self.__get_distro_release(pkg_doc)

    def get_version(self, name, repo=None):
        if not self.has_package(name, repo):
            raise Exception(_('Package \"{}\" not found.').format(name))

        pkg_doc = xmlext.parseString(self.pdb.get_item(name, repo))

        return self.__get_version(pkg_doc)

    def get_summary(self, name, repo=None):
        if not self.has_package(name, repo):
            raise Exception(_('Package \"{}\" not found.').format(name))

        pkg_doc = xmlext.parseString(self.pdb.get_item(name, repo))

        return self.__get_summary(pkg_doc)

    def get_release(self, name, repo=None):
        if not self.has_package(name, repo):
            raise Exception(_('Package \"{}\" not found.').format(name))

        pkg_doc = xmlext.parseString(self.pdb.get_item(name, repo))

        return self.__get_release(pkg_doc)

    def get_last_date(self, name, repo=None):
        if not self.has_package(name, repo):
            raise Exception(_('Package \"{}\" not found.').format(name))

        pkg_doc = xmlext.parseString(self.pdb.get_item(name, repo))

        return self.__get_last_date(pkg_doc)

    def get_package_repo(self, name, repo=None):
        pkg, repo = self.pdb.get_item_repo(name, repo)
        package = inary.data.metadata.Package()
        package.parse(pkg)
        return package, repo

    def which_repo(self, name):
        return self.pdb.which_repo(name)

    def get_obsoletes(self, repo=None):
        return self.odb.get_list_item(repo)

    @staticmethod
    def get_isa_packages(isa):
        repodb = inary.db.repodb.RepoDB()

        packages = set()
        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            for package in xmlext.getTagByName(doc, "Package"):
                if xmlext.getNodeText(package, "IsA"):
                    for node in xmlext.getTagByName(package, "IsA"):
                        if xmlext.getNodeText(node) == isa:
                            packages.add(xmlext.getNodeText(package, "Name"))

        return list(packages)

    def get_rev_deps(self, name, repo=None):
        try:
            rvdb = self.rvdb.get_item(name, repo)
        except BaseException:  # FIXME: what exception could we catch here, replace with that.
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

    # replacesdb holds the info about the replaced packages (ex. gaim ->
    # pidgin)
    def get_replaces(self, repo=None):
        pairs = {}

        for pkg_name in self.rpdb.get_list_item():
            xml = self.pdb.get_item(pkg_name, repo)
            package = xmlext.parseString(str(xml))
            replaces_tag = xmlext.getNode(package, "Replaces")
            if replaces_tag:
                for node in xmlext.getTagByName(replaces_tag, "Package"):
                    r = inary.data.relation.Relation()
                    # XXX Is there a better way to do this?
                    r.decode(node, [])
                    if inary.data.replace.installed_package_replaced(r):
                        pairs.setdefault(r.package, []).append(pkg_name)

        return pairs

    def list_packages(self, repo=None):
        return self.pdb.get_item_keys(repo)

    def list_newest(self, repo, since=None, historydb=None):
        packages = []
        if not historydb:
            historydb = inary.db.historydb.HistoryDB()
        if since:
            since_date = datetime.datetime(
                *time.strptime(since, "%Y-%m-%d")[0:6])
        else:
            since_date = datetime.datetime(
                *time.strptime(historydb.get_last_repo_update(), "%Y-%m-%d")[0:6])

        for pkg in self.list_packages(repo):
            failed = False
            try:
                enter_date = datetime.datetime(
                    *time.strptime(self.get_last_date(pkg, repo), "%m-%d-%Y")[0:6])
            except BaseException:
                failed = True
            if failed:
                try:
                    enter_date = datetime.datetime(
                        *time.strptime(self.get_last_date(pkg, repo), "%Y-%m-%d")[0:6])
                except BaseException:
                    enter_date = datetime.datetime(
                        *time.strptime(self.get_last_date(pkg, repo), "%Y-%d-%m")[0:6])

            if enter_date >= since_date:
                packages.append(pkg)
        return packages

# -*- coding: utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE
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
import os

# Inary Modules
import inary.uri
import inary.errors
import inary.util as util
import inary.context as ctx
from inary.file import File
import inary.db.lazydb as lazydb

# AutoXML Library
import inary.sxml.xmlext as xmlext

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


"""
xmlext içine tag için remove eklenene kadar böyle
"""


class RepoError(inary.errors.Error):
    pass


class IncompatibleRepoError(RepoError):
    pass


class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri


medias = (cd, usb, remote, local) = list(range(4))


class RepoOrder:
    def __init__(self):
        self._doc = None
        self.repos = self._get_repos()

    def add(self, repo_name, repo_url, repo_type="remote"):
        repo_doc = self._get_doc()

        repo_node = xmlext.addNode(repo_doc, "Repo")

        xmlext.addText(repo_node, "Name", repo_name)

        xmlext.addText(repo_node, "Url", repo_url)

        xmlext.addText(repo_node, "Status", "active")

        xmlext.addText(repo_node, "Media", repo_type)

        self._update(repo_doc)

    def set_status(self, repo_name, status):
        repo_doc = self._get_doc()
        for r in xmlext.getTagByName(repo_doc, "Repo"):
            if xmlext.getNodeText(r, "Name") == repo_name:
                status_node = xmlext.getNode(r, "Status")
                if status_node:
                    xmlext.removeChild(status_node, r)
                    xmlext.addText(r, "Status", status)
                else:
                    xmlext.addText(r, "Status", status)

        self._update(repo_doc)

    def get_status(self, repo_name):
        repo_doc = self._get_doc()
        for r in xmlext.getTagByName(repo_doc, "Repo"):
            if xmlext.getNodeText(r, "Name") == repo_name:
                status_node = xmlext.getNode(r, "Status")
                if status_node:
                    status = xmlext.getNodeText(status_node)
                    if status in ["active", "inactive"]:
                        return status

        return "inactive"

    def remove(self, repo_name):
        repo_doc = self._get_doc()
        for r in xmlext.getChildElts(repo_doc):
            if xmlext.getNodeText(r, "Name") == repo_name:
                xmlext.removeChild(r, repo_doc)

        self._update(repo_doc)

    def get_order(self):
        order = []

        # FIXME: get media order from inary.conf
        for m in ["cd", "usb", "remote", "local"]:
            if m in self.repos:
                order.extend(self.repos[m])

        return order

    def _update(self, doc):
        repos_file = os.path.join(ctx.config.info_dir(), ctx.const.repos)
        open(repos_file, "w").write("{}\n".format(xmlext.toPretty(doc)))

        self._doc = None
        self.repos = self._get_repos()

    def _get_doc(self):
        if self._doc is None:
            repos_file = os.path.join(ctx.config.info_dir(), ctx.const.repos)
            if os.path.exists(repos_file):
                self._doc = xmlext.parse(repos_file)

            else:
                self._doc = xmlext.newDocument("REPOS")

        return self._doc

    def _get_repos(self):
        repo_doc = self._get_doc()
        order = {}

        for r in xmlext.getTagByName(repo_doc, "Repo"):
            media = xmlext.getNodeText(r, "Media")
            name = xmlext.getNodeText(r, "Name")
            order.setdefault(media, []).append(name)

        return order


class RepoDB(lazydb.LazyDB):

    def init(self):
        self.repoorder = RepoOrder()

    def has_repo(self, name):
        return name in self.list_repos(only_active=False)

    def has_repo_url(self, url, only_active=True):
        return url in self.list_repo_urls(only_active)

    def get_repo_doc(self, repo_name):
        repo = self.get_repo(repo_name)

        index_path = repo.indexuri.get_uri()

        # FIXME Local index files should also be cached.
        if File.is_compressed(index_path) or repo.indexuri.is_remote_file():
            index = os.path.basename(index_path)
            index_path = util.join_path(ctx.config.index_dir(),
                                        repo_name, index)

            if File.is_compressed(index_path):
                index_path = os.path.splitext(index_path)[0]

        if not os.path.exists(index_path):
            #ctx.ui.warning(_("{} repository needs to be updated").format(repo_name))
            return xmlext.newDocument("INARY")

        try:
            return xmlext.parse(index_path)
        except Exception as e:
            raise RepoError(_(
                "Error parsing repository index information: {} \n Index file does not exist or is malformed.").format(
                e))

    def get_repo(self, repo):
        return Repo(inary.uri.URI(self.get_repo_url(repo)))

    # FIXME: this method is a quick hack around repo_info.indexuri.get_uri()
    def get_repo_url(self, repo):
        urifile_path = util.join_path(ctx.config.index_dir(), repo, "uri")
        uri = open(urifile_path).read()
        return uri.rstrip()

    def add_repo(self, name, repo_info, at=None):
        repo_path = util.join_path(ctx.config.index_dir(), name)
        ###########
        try:
            os.makedirs(repo_path)
        except BaseException:
            pass
        # FIXME: FileExistError errno: 17
        # When addind repo there are the same as name empty dirs it should
        # remove it
        urifile_path = util.join_path(ctx.config.index_dir(), name, "uri")
        open(urifile_path, "w").write(repo_info.indexuri.get_uri())
        self.repoorder.add(name, repo_info.indexuri.get_uri())

    def remove_repo(self, name):
        util.clean_dir(os.path.join(ctx.config.index_dir(), name))
        self.repoorder.remove(name)

    def get_source_repos(self, only_active=True):
        repos = []

        for r in self.list_repos(only_active):
            if xmlext.getNode(self.get_repo_doc(r), "SpecFile"):
                repos.append(r)

        return repos

    def get_binary_repos(self, only_active=True):
        repos = []

        for r in self.list_repos(only_active):
            if not xmlext.getNode(self.get_repo_doc(r), "SpecFile"):
                repos.append(r)

        return repos

    def list_repos(self, only_active=True):
        temp = []
        for x in self.repoorder.get_order():
            if not only_active:
                temp.append(x)
            elif self.repo_active(x):
                temp.append(x)
        return temp

    def list_repo_urls(self, only_active=True):
        repos = []
        for r in self.list_repos(only_active):
            repos.append(self.get_repo_url(r))
        return repos

    def get_repo_by_url(self, url):
        if not self.has_repo_url(url):
            return None

        for r in self.list_repos(only_active=False):
            if self.get_repo_url(r) == url:
                return r

    def activate_repo(self, name):
        self.repoorder.set_status(name, "active")

    def deactivate_repo(self, name):
        self.repoorder.set_status(name, "inactive")

    def repo_active(self, name):
        return self.repoorder.get_status(name) == "active"

    def get_distribution(self, name):
        doc = self.get_repo_doc(name)
        distro = xmlext.getNode(doc, "Distribution")
        return distro and xmlext.getNodeText(distro, "SourceName")

    def get_distribution_release(self, name):
        doc = self.get_repo_doc(name)

        distro = xmlext.getNode(doc, "Distribution")
        return distro and xmlext.getNodeText(distro, "Version")

    def check_distribution(self, name):
        if ctx.get_option('ignore_check'):
            return

        dist_name = self.get_distribution(name)
        if dist_name is None:
            return

        compatible = dist_name == ctx.config.values.general.distribution

        dist_release = self.get_distribution_release(name)
        if dist_release is not None:
            compatible &= \
                dist_release == ctx.config.values.general.distribution_release

        if not compatible:
            self.deactivate_repo(name)
            raise IncompatibleRepoError(
                _("Repository \"{}\" is not compatible with your distribution. Repository is disabled.\nYour distribution is {} release {}\nRepository distribution is {} release {}\n\nIf you want add this repository please use \"--ignore-check\" parameter with this command.").format(name,
                                                                                                                                                                                                                                                                                            ctx.config.values.general.distribution,
                                                                                                                                                                                                                                                                                            ctx.config.values.general.distribution_release,
                                                                                                                                                                                                                                                                                            dist_name,
                                                                                                                                                                                                                                                                                            dist_release))

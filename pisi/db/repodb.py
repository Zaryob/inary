# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2010, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import os

import piksemel

import pisi
import pisi.uri
import pisi.util
import pisi.context as ctx
import pisi.db.lazydb as lazydb
from pisi.file import File

class RepoError(pisi.Error):
    pass

class IncompatibleRepoError(RepoError):
    pass

class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri

medias = (cd, usb, remote, local) = range(4)

class RepoOrder:

    def __init__(self):
        self._doc = None
        self.repos = self._get_repos()

    def add(self, repo_name, repo_url, repo_type="remote"):
        repo_doc = self._get_doc()

        try:
            node = [x for x in repo_doc.tags("Repo")][-1]
            repo_node = node.appendTag("Repo")
        except IndexError:
            repo_node = repo_doc.insertTag("Repo")

        name_node = repo_node.insertTag("Name")
        name_node.insertData(repo_name)

        url_node = repo_node.insertTag("Url")
        url_node.insertData(repo_url)

        name_node = repo_node.insertTag("Status")
        name_node.insertData("active")

        media_node = repo_node.insertTag("Media")
        media_node.insertData(repo_type)

        self._update(repo_doc)

    def set_status(self, repo_name, status):
        repo_doc = self._get_doc()

        for r in repo_doc.tags("Repo"):
            if r.getTagData("Name") == repo_name:
                status_node = r.getTag("Status")
                if status_node:
                    status_node.firstChild().hide()
                    status_node.insertData(status)
                else:
                    status_node = r.insertTag("Status")
                    status_node.insertData(status)

        self._update(repo_doc)

    def get_status(self, repo_name):
        repo_doc = self._get_doc()
        for r in repo_doc.tags("Repo"):
            if r.getTagData("Name") == repo_name:
                status_node = r.getTag("Status")
                if status_node:
                    status = status_node.firstChild().data()
                    if status in ["active", "inactive"]:
                        return status
        return "inactive"

    def remove(self, repo_name):
        repo_doc = self._get_doc()

        for r in repo_doc.tags("Repo"):
            if r.getTagData("Name") == repo_name:
                r.hide()

        self._update(repo_doc)

    def get_order(self):
        order = []

        #FIXME: get media order from pisi.conf
        for m in ["cd", "usb", "remote", "local"]:
            if self.repos.has_key(m):
                order.extend(self.repos[m])

        return order

    def _update(self, doc):
        repos_file = os.path.join(ctx.config.info_dir(), ctx.const.repos)
        open(repos_file, "w").write("%s\n" % doc.toPrettyString())
        self._doc = None
        self.repos = self._get_repos()

    def _get_doc(self):
        if self._doc is None:
            repos_file = os.path.join(ctx.config.info_dir(), ctx.const.repos)
            if os.path.exists(repos_file):
                self._doc = piksemel.parse(repos_file)
            else:
                self._doc = piksemel.newDocument("REPOS")

        return self._doc

    def _get_repos(self):
        repo_doc = self._get_doc()
        order = {}

        for r in repo_doc.tags("Repo"):
            media = r.getTagData("Media")
            name = r.getTagData("Name")
            status = r.getTagData("Status")
            order.setdefault(media, []).append(name)

        return order

class RepoDB(lazydb.LazyDB):

    def init(self):
        self.repoorder = RepoOrder()

    def has_repo(self, name):
        return name in self.list_repos(only_active=False)

    def has_repo_url(self, url, only_active = True):
        return url in self.list_repo_urls(only_active)

    def get_repo_doc(self, repo_name):
        repo = self.get_repo(repo_name)

        index_path = repo.indexuri.get_uri()

        #FIXME Local index files should also be cached.
        if File.is_compressed(index_path) or repo.indexuri.is_remote_file():
            index = os.path.basename(index_path)
            index_path = pisi.util.join_path(ctx.config.index_dir(),
                                             repo_name, index)

            if File.is_compressed(index_path):
                index_path = os.path.splitext(index_path)[0]

        if not os.path.exists(index_path):
            ctx.ui.warning(_("%s repository needs to be updated") % repo_name)
            return piksemel.newDocument("PISI")

        try:
            return piksemel.parse(index_path)
        except Exception, e:
            raise RepoError(_("Error parsing repository index information. Index file does not exist or is malformed."))

    def get_repo(self, repo):
        return Repo(pisi.uri.URI(self.get_repo_url(repo)))

    #FIXME: this method is a quick hack around repo_info.indexuri.get_uri()
    def get_repo_url(self, repo):
        urifile_path = pisi.util.join_path(ctx.config.index_dir(), repo, "uri")
        uri = open(urifile_path, "r").read()
        return uri.rstrip()

    def add_repo(self, name, repo_info, at = None):
        repo_path = pisi.util.join_path(ctx.config.index_dir(), name)
        os.makedirs(repo_path)
        urifile_path = pisi.util.join_path(ctx.config.index_dir(), name, "uri")
        open(urifile_path, "w").write(repo_info.indexuri.get_uri())
        self.repoorder.add(name, repo_info.indexuri.get_uri())

    def remove_repo(self, name):
        pisi.util.clean_dir(os.path.join(ctx.config.index_dir(), name))
        self.repoorder.remove(name)

    def get_source_repos(self, only_active=True):
        repos = []
        for r in self.list_repos(only_active):
            if self.get_repo_doc(r).getTag("SpecFile"):
                repos.append(r)
        return repos

    def get_binary_repos(self, only_active=True):
        repos = []
        for r in self.list_repos(only_active):
            if not self.get_repo_doc(r).getTag("SpecFile"):
                repos.append(r)
        return repos

    def list_repos(self, only_active=True):
        return filter(lambda x:True if not only_active else self.repo_active(x), self.repoorder.get_order())

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
        distro = doc.getTag("Distribution")
        return distro and distro.getTagData("SourceName")

    def get_distribution_release(self, name):
        doc = self.get_repo_doc(name)
        distro = doc.getTag("Distribution")
        return distro and distro.getTagData("Version")

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
                    _("Repository '%s' is not compatible with your "
                      "distribution. Repository is disabled.") % name)

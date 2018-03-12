# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import os

import xml.dom.minidom as minidom
from xml.parsers.expat import ExpatError

import inary
import inary.uri
import inary.util
import inary.context as ctx
import inary.db.lazydb as lazydb
from inary.file import File

class RepoError(inary.Error):
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

        try:
            #FIXME:Burada bir sakatlık çıkacak
            node = [x for x in repo_doc.getElementsByTagName("Repo")][-1]
            repo_node = node.createElement("Repo")
        except ExpatError as err:
            raise("Can not created Repo tag: {}".format(err))

        name_node = repo_node.createElement("Name")
        name_node.appendChild(node.createTextNode(repo_name))
        repo_node.appendChild(name_node)

        url_node = repo_node.createElement("Url")
        url_node.appendChild(node.createTextNode(repo_url))
        repo_node.appendChild(url_node)

        status_node = repo_node.createElement("Status")
        status_node.appendChild(node.createTextNode("active"))
        repo_node.appendChild(status_node)

        media_node = repo_node.createElement("Media")
        media_node.appendChild(node.createTextNode(repo_type))
        repo_node.appendChild(media_node)

        self._update(repo_doc)

    def set_status(self, repo_name, status):
        repo_doc = self._get_doc()

        for r in repo_doc.getElementsByTagName("Repo"):
            if r.getElementsByTagName("Name")[0].firstChild.data == repo_name:
                status_node = r.getElementsByTagName("Status")[0].firstChild.data
                #FIXME: Program burda göt olacak
                if status_node:
                    status_node.childNodes[0].hide()
                    status_node.insertData(status)
                else:
                    status_node = r.insertTag("Status")
                    status_node.insertData(status)

        self._update(repo_doc)

    def get_status(self, repo_name):
        repo_doc = self._get_doc()
        for r in repo_doc.getElementsByTagName("Repo"):
            if r.getElementsByTagName("Name")[0].firstChild.data == repo_name:
                status_node = r.getElementsByTagName("Status")
                if status_node:
                    status = status_node[0].childNodes[0].data
                    if status in ["active", "inactive"]:
                        return status
        return "inactive"

    def remove(self, repo_name):
        repo_doc = self._get_doc()

        for r in repo_doc.getElementsByTagName("Repo"):
            if r.getElementsByTagName("Name")[0].firstChild.data == repo_name:
                r.hide()

        self._update(repo_doc)

    def get_order(self):
        order = []

        #FIXME: get media order from inary.conf
        for m in ["cd", "usb", "remote", "local"]:
            if m in self.repos:
                order.extend(self.repos[m])

        return order

    def _update(self, doc):
        repos_file = os.path.join(ctx.config.info_dir(), ctx.const.repos)
        open(repos_file, "w").write("{}\n".format(doc.toprettyxml()))
        self._doc = None
        self.repos = self._get_repos()

    def _get_doc(self):
        if self._doc is None:
            repos_file = os.path.join(ctx.config.info_dir(), ctx.const.repos)
            if os.path.exists(repos_file):
                self._doc = minidom.parse(repos_file).documentElement
            else:
                impl = minidom.getDOMImplementation()
                dom = impl.createDocument(None, "REPOS", None)
                self._doc = dom.documentElement

        return self._doc

    def _get_repos(self):
        repo_doc = self._get_doc()
        order = {}

        for r in repo_doc.getElementsByTagName("Repo"):
            media = r.getElementsByTagName("Media")[0].firstChild.data
            name = r.getElementsByTagName("Name")[0].firstChild.data
            status = r.getElementsByTagName("Status")[0].firstChild.data
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
            index_path = inary.util.join_path(ctx.config.index_dir(),
                                             repo_name, index)

            if File.is_compressed(index_path):
                index_path = os.path.splitext(index_path)[0]

        if not os.path.exists(index_path):
            ctx.ui.warning(_("{} repository needs to be updated").format(repo_name))
            impl = minidom.getDOMImplementation()
            dom = impl.createDocument(None, "INARY", None)
            return dom.documentElement

        try:
            return minidom.parse(index_path)
        except ExpatError as e:
            raise RepoError(_("Error parsing repository index information. Index file does not exist or is malformed."))

    def get_repo(self, repo):
        return Repo(inary.uri.URI(self.get_repo_url(repo)))

    #FIXME: this method is a quick hack around repo_info.indexuri.get_uri()
    def get_repo_url(self, repo):
        urifile_path = inary.util.join_path(ctx.config.index_dir(), repo, "uri")
        uri = open(urifile_path, "r").read()
        return uri.rstrip()

    def add_repo(self, name, repo_info, at = None):
        repo_path = inary.util.join_path(ctx.config.index_dir(), name)
        os.makedirs(repo_path)
        urifile_path = inary.util.join_path(ctx.config.index_dir(), name, "uri")
        open(urifile_path, "w").write(repo_info.indexuri.get_uri())
        self.repoorder.add(name, repo_info.indexuri.get_uri())

    def remove_repo(self, name):
        inary.util.clean_dir(os.path.join(ctx.config.index_dir(), name))
        self.repoorder.remove(name)

    def get_source_repos(self, only_active=True):
        repos = []
        for r in self.list_repos(only_active):
            if self.get_repo_doc(r).getElementsByTagName("SpecFile")[0]:
                repos.append(r)
        return repos

    def get_binary_repos(self, only_active=True):
        repos = []
        for r in self.list_repos(only_active):
            if not self.get_repo_doc(r).getElementsByTagName("SpecFile")[0]:
                repos.append(r)
        return repos

    def list_repos(self, only_active=True):
        temp = []
        for x in self.repoorder.get_order():
            if not only_active:
                temp.append(x)
            elif self.repo_active(x) == True:
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
        distro = doc.getElementsByTagName("Distribution")[0]
        return distro.firstChild.data and distro.getElementsByTagName("SourceName")[0].firstChild.data

    def get_distribution_release(self, name):
        doc = self.get_repo_doc(name)
        distro = doc.getElementsByTagName("Distribution")[0]
        return distro.firstChild.data and distro.getElementsByTagName("Version")[0].firstChild.data

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
                    _("Repository '{}' is not compatible with your distribution. Repository is disabled.").format(name))

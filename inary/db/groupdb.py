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

import inary.context as ctx
import inary.db.repodb
import inary.db.itembyrepo
import inary.data.group as Group
import inary.db.lazydb as lazydb

class GroupNotFound(Exception):
    pass

class GroupDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)

    def init(self):
        group_nodes = {}
        group_components = {}

        try:
            import ciksemel
            self.parser = "ciksemel"
        except:
            self.parser = "minidom"

        repodb = inary.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            group_nodes[repo] = self.__generate_groups(doc)
            group_components[repo] = self.__generate_components(doc)

        self.gdb = inary.db.itembyrepo.ItemByRepo(group_nodes)
        self.gcdb = inary.db.itembyrepo.ItemByRepo(group_components)

    def __generate_components(self, doc):
        groups = {}

        if self.parser=="ciksemel":
            for c in doc.tags("Component"):
                group = c.getTagData("Group")
                if not group:
                    group = "unknown"
                groups.setdefault(group, []).append(c.getTagData("Name"))

        else:
            for c in doc.childNodes:
                if c.nodeType == c.ELEMENT_NODE and c.tagName == "Component":
                    group = c.getElementsByTagName("Group")[0]
                    if not group:
                        group = "unknown"
                    groups.setdefault(group.firstChild.data, []).append(c.getElementsByTagName("Name")[0].firstChild.data)
        return groups

    def __generate_groups(self, doc):

        if self.parser=="ciksemel":
            return dict([(x.getTagData("Name"), x.toString()) for x in doc.tags("Group")])

        else:
            return dict([(x.getElementsByTagName("Name")[0].firstChild.data, x.toxml()) \
            for x in doc.childNodes if x.nodeType == x.ELEMENT_NODE and x.tagName == "Group"])

    def has_group(self, name, repo = None):
        return self.gdb.has_item(name, repo)

    def list_groups(self, repo=None):
        return self.gdb.get_item_keys(repo)

    def get_group(self, name, repo = None):

        if not self.has_group(name, repo):
            raise GroupNotFound(_('Group {} not found').format(name))

        group = Group.Group()
        group.parse(self.gdb.get_item(name, repo))

        return group

    def get_group_components(self, name, repo=None):
        if not self.has_group(name, repo):
            raise GroupNotFound(_('Group {} not found').format(name))

        if self.gcdb.has_item(name):
            return self.gcdb.get_item(name, repo)

        return []

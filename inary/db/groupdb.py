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

# Inary Modules
import inary.db.repodb
import inary.db.itembyrepo
import inary.db.lazydb as lazydb
import inary.data.group as Group

# AutoXML Library
from inary.sxml import xmlext

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class GroupNotFound(Exception):
    pass


class GroupDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)

    def init(self):
        group_nodes = {}
        group_components = {}

        repodb = inary.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            group_nodes[repo] = self.__generate_groups(doc)
            group_components[repo] = self.__generate_components(doc)

        self.gdb = inary.db.itembyrepo.ItemByRepo(group_nodes)
        self.gcdb = inary.db.itembyrepo.ItemByRepo(group_components)

    @staticmethod
    def __generate_components(doc):
        groups = {}
        components = xmlext.getTagByName(doc, "Component")
        for comp in components:
            group = xmlext.getNodeText(comp, "Group")
            name = xmlext.getNodeText(comp, "Name")
            groups.setdefault(group, []).append(name)

        return groups

    @staticmethod
    def __generate_groups(doc):
        groups = {}
        group = xmlext.getTagByName(doc, "Group")
        for gr in group:
            name = xmlext.getNodeText(gr, "Name")
            groups[name] = xmlext.toString(gr)

        return groups

    def has_group(self, name, repo=None):
        return self.gdb.has_item(name, repo)

    def list_groups(self, repo=None):
        return self.gdb.get_item_keys(repo)

    def get_group(self, name, repo=None):

        if not self.has_group(name, repo):
            raise GroupNotFound(_('Group \"{}\" not found.').format(name))

        group = Group.Group()
        group.parse(self.gdb.get_item(name, repo))

        return group

    def get_group_components(self, name, repo=None):
        if not self.has_group(name, repo):
            raise GroupNotFound(_('Group \"{}\" not found.').format(name))

        if self.gcdb.has_item(name):
            return self.gcdb.get_item(name, repo)

        return []

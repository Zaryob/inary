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
import gzip

# Inary Modules
import inary.db

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class ItemByRepo:
    def __init__(self, dbobj, compressed=False):
        self.dbobj = dbobj
        self.compressed = compressed

    def has_repo(self, repo):
        return repo in self.dbobj

    def has_item(self, item, repo=None):
        for r in self.item_repos(repo):
            if r in self.dbobj and item in self.dbobj[r]:
                return True

        return False

    def which_repo(self, item):
        for r in inary.db.repodb.RepoDB().list_repos():
            if r in self.dbobj and item in self.dbobj[r]:
                return r

        raise Exception(
            _("\"{}\" not found in any repository.").format(
                str(item)))

    def get_item_repo(self, item, repo=None):
        for r in self.item_repos(repo):
            if r in self.dbobj and item in self.dbobj[r]:
                if self.compressed:
                    return gzip.zlib.decompress(
                        self.dbobj[r][item]).decode('utf-8'), r
                else:
                    return self.dbobj[r][item], r

        raise Exception(_("Repo item \"{}\" not found.").format(str(item)))

    def get_item(self, item, repo=None):
        item, repo = self.get_item_repo(item, repo)
        return item

    def get_item_keys(self, repo=None):
        items = []
        for r in self.item_repos(repo):
            if not self.has_repo(r):
                raise Exception(
                    _('Repository \"{}\" does not exist.').format(repo))

            if r in self.dbobj:
                items.extend(list(self.dbobj[r].keys()))

        return list(set(items))

    def get_list_item(self, repo=None):
        items = []
        for r in self.item_repos(repo):
            if not self.has_repo(r):
                raise Exception(
                    _('Repository \"{}\" does not exist.').format(repo))

            if r in self.dbobj:
                items.extend(self.dbobj[r])

        return list(set(items))

    def get_items_iter(self, repo=None):
        for r in self.item_repos(repo):
            if not self.has_repo(r):
                raise Exception(
                    _('Repository \"{}\" does not exist.').format(repo))

            if self.compressed:
                for item in list(self.dbobj[r].keys()):
                    yield str(item), gzip.zlib.decompress(self.dbobj[r][item]).decode('utf-8')
            else:
                for item in list(self.dbobj[r].keys()):
                    yield str(item), str(self.dbobj[r][item])

    def item_repos(self, repo=None):
        if repo:
            repos = [repo]
            return repos
        else:
            return inary.db.repodb.RepoDB().list_repos()

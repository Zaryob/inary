# -*- coding: utf-8 -*-
#
# Copyright (C) 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import gzip
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.db

class ItemByRepo:
    def __init__(self, dbobj, compressed=False):
        self.dbobj = dbobj
        self.compressed = compressed
        self.repodb = pisi.db.repodb.RepoDB()

    def has_repo(self, repo):
        return self.dbobj.has_key(repo)

    def has_item(self, item, repo=None):
        for r in self.item_repos(repo):
            if self.dbobj.has_key(r) and self.dbobj[r].has_key(item):
                return True

        return False

    def which_repo(self, item):
        for r in self.repodb.list_repos():
            if self.dbobj.has_key(r) and self.dbobj[r].has_key(item):
                return r

        raise Exception(_("%s not found in any repository.") % str(item))

    def get_item_repo(self, item, repo=None):
        for r in self.item_repos(repo):
            if self.dbobj.has_key(r) and self.dbobj[r].has_key(item):
                if self.compressed:
                    return gzip.zlib.decompress(self.dbobj[r][item]), r
                else:
                    return self.dbobj[r][item], r

        raise Exception(_("Repo item %s not found") % str(item))

    def get_item(self, item, repo=None):
        item, repo = self.get_item_repo(item, repo)
        return item

    def get_item_keys(self, repo=None):
        items = []
        for r in self.item_repos(repo):
            if not self.has_repo(r):
                raise Exception(_('Repository %s does not exist.') % repo)

            if self.dbobj.has_key(r):
                items.extend(self.dbobj[r].keys())

        return list(set(items))

    def get_list_item(self, repo=None):
        items = []
        for r in self.item_repos(repo):
            if not self.has_repo(r):
                raise Exception(_('Repository %s does not exist.') % repo)

            if self.dbobj.has_key(r):
                items.extend(self.dbobj[r])

        return list(set(items))

    def get_items_iter(self, repo=None):
        for r in self.item_repos(repo):
            if not self.has_repo(r):
                raise Exception(_('Repository %s does not exist.') % repo)

            if self.compressed:
                for item in self.dbobj[r].keys():
                    yield item, gzip.zlib.decompress(self.dbobj[r][item])
            else:
                for item in self.dbobj[r].keys():
                    yield item, self.dbobj[r][item]
        
    def item_repos(self, repo=None):
        repos = self.repodb.list_repos()
        if repo:
            repos = [repo]
        return repos

# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import re
import shelve
import hashlib

import inary
import inary.util as util
import inary.context as ctx
import inary.db.lazydb as lazydb

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# FIXME:
# We could traverse through files.xml files of the packages to find the path and
# the package - a linear search - as some well known package managers do. But the current
# file conflict mechanism of inary prevents this and needs a fast has_file function.
# So currently filesdb is the only db and we cant still get rid of rebuild-db :/

class FilesDB(lazydb.LazyDB):

    def __init__(self):
        self.filesdb = {}
        self.__check_filesdb()

    def __del__(self):
        self.close()

    def create_filesdb(self):
        ctx.ui.info(inary.util.colorize(_('Creating files database...'), 'blue'))
        installdb = inary.db.installdb.InstallDB()
        for pkg in installdb.list_installed():
            files = installdb.get_files(pkg)
            self.add_files(pkg, files)
        ctx.ui.info(inary.util.colorize(_('Added files database...'), 'blue'))

    def get_file(self, path):
        key=hashlib.md5(path.encode('utf-8')).hexdigest()
        return self.filesdb.get(key), path

    def search_file(self, term):
        pkg, path = self.get_file(term)
        if pkg:
            return [(pkg,[path])]

        installdb = inary.db.installdb.InstallDB()
        found = []
        for pkg in installdb.list_installed():
            files_xml = open(os.path.join(installdb.package_path(pkg), ctx.const.files_xml)).read()
            paths = re.compile('<Path>(.*?%s.*?)</Path>' % re.escape(term), re.I).findall(files_xml)
            if paths:
                found.append((pkg, paths))
        return found

    def add_files(self, pkg, files):
        self.__check_filesdb()
        ctx.ui.info("%-80.80s\r" % (util.colorize(_('-> Adding \'{}\' to db...'), 'purple').format(pkg)), noln=True)
        for f in files.list:
            key=hashlib.md5(f.path.encode('utf-8')).hexdigest()
            self.filesdb[key] = pkg

    def remove_files(self, files):
        for f in files:
            key=bytes(hashlib.md5(f.path.encode('utf-8')).hexdigest())
            if hashlib.md5(key).hexdigest() in self.filesdb:
                del self.filesdb[key]

    def destroy(self):
        files_db = os.path.join(ctx.config.info_dir(), ctx.const.files_db)
        if os.path.exists(files_db):
            os.unlink(files_db)

    def close(self):
        if isinstance(self.filesdb, shelve.DbfilenameShelf):
            self.filesdb.close()

    def __check_filesdb(self):
        if isinstance(self.filesdb, shelve.DbfilenameShelf):
            return

        files_db = os.path.join(ctx.config.info_dir(), ctx.const.files_db)

        if not os.path.exists(files_db):
            flag = "n"
        elif os.access(files_db, os.W_OK):
            flag = "w"
        else:
            flag = "r"

        self.filesdb = shelve.open(files_db, flag)
        if flag == "n":
            self.create_filesdb()

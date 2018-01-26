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

import os
import re
import hashlib
try:
   import shelve
except ImportError:
   raise Exception(_("FilesDB broken: Shelve module not imported."))


import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.db.lazydb as lazydb
import inary.context as ctx

# FIXME:
# We could traverse through files.xml files of the packages to find the path and
# the package - a linear search - as some well known package managers do. But the current 
# file conflict mechanism of inary prevents this and needs a fast has_file function. 
# So currently filesdb is the only db and we cant still get rid of rebuild-db :/

class FilesDB(lazydb.LazyDB):
    def __init__(self):
        self.filesdb={}
        self.filesdb_path = os.path.join(ctx.config.info_dir(), ctx.const.files_db)
        #if not [f for f in os.listdir(self.filesdb_path) if f.endswith('.db')]:
        #    if ctx.scom: self.destroy()
        #    self.create_filesdb()

        if isinstance(self.filesdb, shelve.DbfilenameShelf):
            return

        if not os.path.exists(self.filesdb_path):
            flag = "n"
        elif os.access(self.filesdb_path, os.W_OK):
            flag = "w"
        else:
            flag = "r"

        self.filesdb = shelve.open(self.filesdb_path, flag=flag)

    def __del__(self):
        self.close()

    def create_filesdb(self):
        ctx.ui.info(inary.util.colorize(_('Creating files database...'), 'blue'))
        installdb = inary.db.installdb.InstallDB()
        for pkg in installdb.list_installed():
            ctx.ui.info(inary.util.colorize(_('  ---> Adding \'{}\' to db... '), 'purple').format(pkg), noln= True)
            files = installdb.get_files(pkg)
            self.add_files(pkg, files)
            ctx.ui.info(inary.util.colorize(_('OK.'), 'backgroundmagenta'))
        ctx.ui.info(inary.util.colorize(_('Added files database...'), 'blue'))

    def has_file(self, path):
        key= str(hashlib.md5(path.encode('utf-8')).digest())
        return key in self.filesdb

    def get_file(self, path):
        key= str(hashlib.md5(path.encode('utf-8')).digest())
        return self.filesdb[key], path

    def search_file(self, term):
        if self.has_file(term):
            pkg, path = self.get_file(term)
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
        for f in files.list:
            print(f)
            key= str(hashlib.md5(f.path.encode('utf-8')).digest())
            value= str(pkg.encode('utf-8'))
            self.filesdb[key] = value

    def remove_files(self, files):
        for f in files:
            key= str(hashlib.md5(f.path.encode('utf-8')).digest())
            if key in self.filesdb:
                del self.filesdb[key]

    def destroy(self):
        self.filesdb_path = os.path.join(ctx.config.info_dir(), ctx.const.files_db)
        ctx.ui.info(inary.util.colorize(_('Cleaning files database folder...  '), 'green'), noln=True)
        if os.path.exists(self.filesdb_path):
            os.unlink(self.filesdb_path)
        ctx.ui.info(inary.util.colorize(_('done.'), 'green'))

    def close(self):
        if isinstance(self.filesdb, shelve.DbfilenameShelf):
            self.filesdb.close()

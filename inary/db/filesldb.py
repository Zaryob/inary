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

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.context as ctx

class FilesLDB():
    def __init__(self):
        try:
            import plyvel
        except ImportError:
            raise ImportError(_("LevelDB not found! Please install LevelDB and plyvel!"))
        self.files_ldb_path = os.path.join(ctx.config.info_dir(), ctx.const.files_ldb)
        self.filesdb = plyvel.DB(self.files_ldb_path, create_if_missing=True)
        if not [f for f in os.listdir(self.files_ldb_path) if f.endswith('.ldb')]:
            if ctx.scom: self.destroy()
            self.create_filesdb()

    def __del__(self):
        self.close()

    def create_filesdb(self):
        ctx.ui.info(inary.util.colorize(_('Creating files database...'), 'blue'))
        installdb = inary.db.installdb.InstallDB()
        for pkg in installdb.list_installed():
            #ctx.ui.info(inary.util.colorize(_('  ---> Adding \'{}\' to db... '), 'purple')¿format(pkg), noln= True)
            files = installdb.get_files(pkg)
            self.add_files(pkg, files)
            #ctx.ui.info(inary.util.colorize(_('OK.'), 'backgroundmagenta'))
        ctx.ui.info(inary.util.colorize(_('Added files database...'), 'blue'))

    def get_file(self, path):
        return self.filesdb.get(hashlib.md5(path.encode('utf-8')).digest()), path

    def search_file(self, term):
        pkg, path = self.get_file(term)
        if pkg:
            return [(pkg,[path])]

        installdb = inary.db.installdb.InstallDB()
        found = []
        for pkg in installdb.list_installed():
            files_xml = open(os.path.join(installdb.package_path(pkg), ctx.const.files_xml)).read()
            paths = re.compile('<Path>(.*?{}.*?)</Path>'.format(re.escape(term)), re.I).findall(files_xml)
            if paths:
                found.append((pkg, paths))
        return found

    def add_files(self, pkg, files):
        for f in files.list:
            key=bytes(hashlib.md5(f.path.encode('utf-8')).digest())
            value= bytes(pkg.encode('utf-8'))
            self.filesdb.put(key=key, value=value)

    def remove_files(self, files):
        for f in files:
            self.filesdb.delete(bytes(hashlib.md5(f.path.encode('utf-8')).digest()))

    def destroy(self):
        ctx.ui.info(inary.util.colorize(_('Cleaning files database folder... '), 'green'), noln=True)
        for f in os.listdir(self.files_ldb_path): os.unlink(os.path.join(self.files_ldb_path, f))
        ctx.ui.info(inary.util.colorize(_('done.'), 'green'))

    def close(self):
        if not self.filesdb.closed: self.filesdb.close()

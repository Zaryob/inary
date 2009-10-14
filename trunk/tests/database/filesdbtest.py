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

import testcase
import pisi

class FilesDBTestCase(testcase.TestCase):

    filesdb = pisi.db.filesdb.FilesDB()

    def testHasFile(self):
        assert not self.filesdb.has_file("usr/bin/ethtool")
        pisi.api.install(["ethtool"])
        assert self.filesdb.has_file("usr/bin/ethtool")
        pisi.api.remove(["ethtool"])
        assert not self.filesdb.has_file("usr/bin/ethtool")

    def testGetFile(self):
        pisi.api.install(["ethtool"])
        pkg, path = self.filesdb.get_file("usr/bin/ethtool")
        assert pkg == "ethtool"
        assert path == "usr/bin/ethtool"
        pisi.api.remove(["ethtool"])
        assert not self.filesdb.has_file("usr/bin/ethtool")

    def testAddRemoveFiles(self):
        fileinfo1 = pisi.files.FileInfo()
        fileinfo1.path = "etc/pisi/pisi.conf"
        fileinfo2 = pisi.files.FileInfo()
        fileinfo2.path = "etc/pisi/mirrors.conf"
        
        files = pisi.files.Files()
        files.list.append(fileinfo1)
        files.list.append(fileinfo2)

        assert not self.filesdb.has_file("etc/pisi/pisi.conf")
        assert not self.filesdb.has_file("etc/pisi/mirrors.conf")

        self.filesdb.add_files("pisi", files)

        assert self.filesdb.has_file("etc/pisi/pisi.conf")
        assert self.filesdb.has_file("etc/pisi/mirrors.conf")

        pkg, path = self.filesdb.get_file("etc/pisi/pisi.conf")
        assert pkg == "pisi"

        # FIXME: inconsistency in filesdb.py add_remove and remove_remove parameters
        self.filesdb.remove_files(files.list)

        assert not self.filesdb.has_file("etc/pisi/pisi.conf")
        assert not self.filesdb.has_file("etc/pisi/mirrors.conf")
        
    def testSearchFile(self):
        assert not self.filesdb.search_file("ethtool")
        pisi.api.install(["ethtool"])
        found = self.filesdb.search_file("ethtool")
        pkg, files = found[0]
        assert set(files) == set(['usr/bin/ethtool'])
        pisi.api.remove(["ethtool"])

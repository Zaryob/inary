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

from . import testcase
import inary

class FilesDBTestCase(testcase.TestCase):

    filesdb = inary.db.filesldb.FilesLDB()

    def testHasFile(self):
        assert not self.filesdb.has_file("bin/bash")
        inary.api.install(["bash"])
        assert self.filesdb.has_file("bin/bash")
        inary.api.remove(["bash"])
        assert not self.filesdb.has_file("bin/bash")

    def testGetFile(self):
        inary.api.install(["bash"])
        pkg, path = self.filesdb.get_file("bin/bash")
        assert pkg == "bash"
        assert path == "bin/bash"
        inary.api.remove(["bash"])
        assert not self.filesdb.has_file("bin/bash")

    def testAddRemoveFiles(self):
        fileinfo1 = inary.files.FileInfo()
        fileinfo1.path = "etc/inary/inary.conf"
        fileinfo2 = inary.files.FileInfo()
        fileinfo2.path = "etc/inary/mirrors.conf"
        
        files = inary.files.Files()
        files.list.append(fileinfo1)
        files.list.append(fileinfo2)

        assert not self.filesdb.has_file("etc/inary/inary.conf")
        assert not self.filesdb.has_file("etc/inary/mirrors.conf")

        self.filesdb.add_files("inary", files)

        assert self.filesdb.has_file("etc/inary/inary.conf")
        assert self.filesdb.has_file("etc/inary/mirrors.conf")

        pkg, path = self.filesdb.get_file("etc/inary/inary.conf")
        assert pkg == "inary"

        # FIXME: inconsistency in filesdb.py add_remove and remove_remove parameters
        self.filesdb.remove_files(files.list)

        assert not self.filesdb.has_file("etc/inary/inary.conf")
        assert not self.filesdb.has_file("etc/inary/mirrors.conf")
        
    def testSearchFile(self):
        assert not self.filesdb.search_file("bash")
        inary.api.install(["bash"])
        found = self.filesdb.search_file("bash")
        pkg, files = found[0]
        assert set(files) == set(['bin/bash'])
        inary.api.remove(["bash"])

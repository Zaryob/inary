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


import inary
import inary.context as ctx
import unittest
from . import testcase


class FilesDBTestCase(testcase.TestCase):

    filesdb = inary.db.filesdb.FilesDB()

    def testHasFile(self):
        self.assertFalse(self.filesdb.has_file("etc/protocols"))
        inary.api.install(["iana-etc"])
        self.assertTrue(self.filesdb.has_file("etc/protocols"))
        self.assertTrue(self.filesdb.has_file("etc/services"))
        inary.api.remove(["iana-etc"])
        self.assertFalse(self.filesdb.has_file("etc/protocols"))

    def testGetFile(self):
        inary.api.install(["iana-etc"])
        pkg, path = self.filesdb.get_file("etc/protocols")
        self.assertEqual(pkg, "iana-etc")
        self.assertEqual(path, "etc/protocols")
        inary.api.remove(["iana-etc"])
        self.assertFalse(self.filesdb.has_file("etc/protocols"))

    def testAddRemoveFiles(self):
        fileinfo1 = inary.data.files.FileInfo()
        fileinfo1.path = "etc/inary/inary.conf"
        fileinfo2 = inary.data.files.FileInfo()
        fileinfo2.path = "etc/inary/mirrors.conf"

        files = inary.data.files.Files()
        files.list.append(fileinfo1)
        files.list.append(fileinfo2)

        self.assertFalse(self.filesdb.has_file("etc/inary/inary.conf"))
        self.assertFalse(self.filesdb.has_file("etc/inary/mirrors.conf"))

        self.filesdb.add_files("inary", files)

        self.assertTrue(self.filesdb.has_file("etc/inary/inary.conf"))
        self.assertTrue(self.filesdb.has_file("etc/inary/mirrors.conf"))

        pkg, path = self.filesdb.get_file("etc/inary/inary.conf")
        self.assertEqual(pkg, "inary")

        # FIXME: inconsistency in filesdb.py add_remove and remove_remove
        # parameters
        self.filesdb.remove_files(files.list)

        self.assertFalse(self.filesdb.has_file("etc/inary/inary.conf"))
        self.assertFalse(self.filesdb.has_file("etc/inary/mirrors.conf"))

    def testSearchFile(self):
        self.assertFalse(self.filesdb.search_file("protocols"))
        inary.api.install(["iana-etc"])
        self.assertTrue(self.filesdb.search_file("protocols"))
        inary.api.remove(["iana-etc"])

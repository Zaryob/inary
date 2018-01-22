#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2010, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import unittest
import database

import inary
import inary.context as ctx

#Database tests
from databaseTests.testRepoDB import RepoDBTestCase
from databaseTests.testPackageDB import PackageDBTestCase
from databaseTests.testSourceDB import SourceDBTestCase
from databaseTests.testInstallDB import InstallDBTestCase
from databaseTests.testComponentDB import ComponentDBTestCase
from databaseTests.testFilesLDB import FilesDBTestCase
from databaseTests.testLazyDB import LazyDBTestCase
from databaseTests.testItembyRepo import ItemByRepoTestCase

#Package Tests
from packageTests.testConflict import ConflictTestCase
from packageTests.testDependency import DependencyTestCase
from packageTests.testFiles import FilesTestCase
from packageTests.testHistory import HistoryTestCase
from packageTests.testMetadata import MetadataTestCase
from packageTests.testPackage import PackageTestCase
from packageTests.testPspec import SpecFileTestCase
from packageTests.relationtest import RelationTestCase
from packageTests.testReplace import ReplaceTestCase

#File Tests
from fileTests.testArchive import ArchiveTestCase
from fileTests.testFile import FileTestCase
from fileTests.testSrcArchive import SourceArchiveTestCase

#Inary Tests
from inaryTests.testConstant import ConstantTestCase
from inaryTests.testConfigFile import ConfigFileTestCase
from inaryTests.testMirrors import MirrorsTestCase
from inaryTests.testShell import ShellTestCase
from inaryTests.testUri import UriTestCase
from inaryTests.testUtil import UtilTestCase
from inaryTests.testVersion import VersionTestCase

#Process Tests
from processTests.testFetch import FetchTestCase

#Type Tests
from typeTests.testOO import OOTestCase
from typeTests.testPgraph import GraphTestCase

# XML tests
from xmlTests.testAutoxml import AutoxmlTestCase

def setup():
    options = inary.config.Options()
    options.destdir = 'repos/tmp'
    inary.api.set_options(options)
    inary.api.set_scom(False)

    ctx.config.values.general.distribution = "Pardus"
    ctx.config.values.general.distribution_release = "2007"


if __name__ == '__main__':
    if os.path.exists("repos/tmp"):
        import shutil
        shutil.rmtree("repos/tmp")

    suite = unittest.TestSuite()
    unittest.main()


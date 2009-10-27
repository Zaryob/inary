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

import unittest
import database

from database.repodbtest import RepoDBTestCase
from database.packagedbtest import PackageDBTestCase
from database.sourcedbtest import SourceDBTestCase
from database.installdbtest import InstallDBTestCase
from database.componentdbtest import ComponentDBTestCase
from database.filesdbtest import FilesDBTestCase
from database.lazydbtest import LazyDBTestCase
from database.itembyrepotest import ItemByRepoTestCase

from archivetests import ArchiveTestCase
from configfiletest import ConfigFileTestCase
from conflicttests import ConflictTestCase
from constanttest import ConstantTestCase
from dependencytest import DependencyTestCase
from fetchtest import FetchTestCase
from filetest import FileTestCase
from filestest import FilesTestCase
from graphtest import GraphTestCase
from historytest import HistoryTestCase
from metadatatest import MetadataTestCase
from mirrorstest import MirrorsTestCase
from packagetest import PackageTestCase
from relationtest import RelationTestCase
from replacetest import ReplaceTestCase
from shelltest import ShellTestCase
from specfiletests import SpecFileTestCase
from srcarchivetest import SourceArchiveTestCase
from uritest import UriTestCase
from utiltest import UtilTestCase
from versiontest import VersionTestCase















suite = unittest.TestSuite()

if __name__ == '__main__':
    unittest.main()

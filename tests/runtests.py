#!/usr/bin/python
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

import pisi
import pisi.context as ctx

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

def setup():
    options = pisi.config.Options()
    options.destdir = 'repos/tmp'
    pisi.api.set_options(options)
    pisi.api.set_comar(False)

    ctx.config.values.general.distribution = "Pardus"
    ctx.config.values.general.distribution_release = "2007"


if __name__ == '__main__':
    if os.path.exists("repos/tmp"):
        import shutil
        shutil.rmtree("repos/tmp")

    suite = unittest.TestSuite()
    unittest.main()


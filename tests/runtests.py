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
from versiontest import VersionTestCase
from mirrorstest import MirrorsTestCase
from relationtest import RelationTestCase

suite = unittest.TestSuite()

if __name__ == '__main__':
    unittest.main()

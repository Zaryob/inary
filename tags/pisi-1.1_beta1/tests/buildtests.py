# -*- coding: utf-8 -*-
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.


import unittest
import shutil

import testcase
from pisi.build import *

class BuildTestCase(testcase.TestCase):
    def setUp(self):
        options = pisi.config.Options()
        options.ignore_build_no = False
        testcase.TestCase.setUp(self, options = options)

    def testBasicBuild(self):
        shutil.copy('tests/buildtests/a/actions.py-1', 'tests/buildtests/a/actions.py')
        pspec = 'tests/buildtests/a/pspec.xml'
        pb = Builder(pspec, None)
        pb.build()
        self.assertEqual(os.path.exists('a-1.0-1-1.pisi'), True)
        shutil.move('a-1.0-1-1.pisi', 'tests/buildtests/a/a-1.0-1-1.pisi')

    def testBuildNumber(self):
        pspec = 'tests/buildtests/a/pspec.xml'
        pb = Builder(pspec, None)

        shutil.copy('tests/buildtests/a/actions.py-2', 'tests/buildtests/a/actions.py')
        pb.build()
        self.assertEqual(os.path.exists('a-1.0-1-2.pisi'), True)

        shutil.copy('tests/buildtests/a/actions.py-3', 'tests/buildtests/a/actions.py')
        pb.build()
        self.assertEqual(os.path.exists('a-1.0-1-3.pisi'), False)
 
        os.remove('tests/buildtests/a/actions.py')
        os.remove('a-1.0-1-2.pisi')
        os.remove('tests/buildtests/a/a-1.0-1-1.pisi')

suite = unittest.makeSuite(BuildTestCase)

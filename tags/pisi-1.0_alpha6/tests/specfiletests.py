# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import os

from pisi import specfile
from pisi.config import config
import pisi.util as util

class SpecFileTestCase(unittest.TestCase):
    def setUp(self):
        self.spec = specfile.SpecFile()
        self.spec.read("tests/popt/pspec.xml")
    
    def testReadSpec(self):
        self.assertEqual(self.spec.source.name, "popt")

        self.assertEqual(self.spec.source.version, "1.7")

        self.assertEqual(self.spec.source.release, "3")

        self.assertEqual(self.spec.source.archiveSHA1,
                "66f3c77b87a160951b180447f4a6dce68ad2f71b")

        patches = self.spec.source.patches
        self.assertEqual(len(patches), 1)
        patch = patches[0] #get first and the only patch
        self.assertEqual(patch.filename, "popt-1.7-uclibc.patch.gz")
        self.assertEqual(patch.compressionType, "gz")

        packages = self.spec.packages
        self.assertEqual(len(packages), 1)
        package = packages[0] # get the first and the only package
        self.assertEqual(package.name, "popt-libs")

        # search for a path in package.paths
        pn = "/usr/lib"
        matched = [p for p in package.paths if p.pathname == pn]
        if not matched:
            self.fail("Failed to match pathname: %s" %pn)

    def testIsAPartOf(self):
        # test existence in Source
        if not "library:util:optparser" in self.spec.source.isa:
            self.fail("Failed to match IsA in Source")
        if not isinstance(self.spec.source.isa, list):
            self.fail("source.isa is not a list, but it must be...")

        if "rpm:archive" != self.spec.source.partof:
            self.fail("Failed to match PartOf in Source")

        # test existence in Package
        pkg = self.spec.packages[0]
        if not "library:util:optparser" in pkg.isa:
            self.fail("Failed to match IsA in Package")
        if not isinstance(pkg.isa, list):
            self.fail("source.isa is not a list, but it must be...")

        if "rpm:archive" != pkg.partof:
            self.fail("Failed to match PartOf in Package")
        
    def testVerify(self):
        if self.spec.has_errors():
            self.fail("Failed to verify specfile")

    def testCopy(self):
        util.check_dir(config.tmp_dir())
        self.spec.read("tests/popt/pspec.xml")
        self.spec.write(os.path.join(config.tmp_dir(), 'popt-copy.pspec.xml'))


suite = unittest.makeSuite(SpecFileTestCase)

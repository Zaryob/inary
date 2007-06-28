# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
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

from pisi import metadata
from pisi import util
from pisi import specfile

class MetaDataTestCase(unittest.TestCase):

    def testRead(self):
        md = metadata.MetaData()
        md.read('tests/popt/metadata.xml')

        self.assertEqual(md.package.license, ["as-is"])

        self.assertEqual(md.package.version, "1.7")

        self.assertEqual(md.package.installedSize, 15982)
        return md

    def testWrite(self):
        md = self.testRead()
        md.write('/tmp/metadata-test.xml')

    def testVerify(self):
        md = self.testRead()
        if md.errors():
            self.fail("Couldn't verify!")

    def testFromSpec(self):
        specmd = metadata.MetaData()
        spec = specfile.SpecFile('tests/popt/pspec.xml')
        specmd.from_spec(spec.source, spec.packages[0], spec.history)
        md = metadata.MetaData()
        md.read('tests/popt/metadata.xml')
        for key in md.package.__dict__.keys():
            if key not in ('installedSize', 'packageFormat', 'distributionRelease',
                           'license', 'architecture', 'distribution', 'partOf'):
                self.assertEqual(md.package.__dict__[key], specmd.package.__dict__[key])

suite = unittest.makeSuite(MetaDataTestCase)

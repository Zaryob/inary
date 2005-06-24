
import unittest
import os

from pisi import specfile
from pisi.config import config
import pisi.util as util

class SpecFileTestCase(unittest.TestCase):
    def setUp(self):
        self.spec = specfile.SpecFile()
        self.spec.read("samples/popt/popt.pspec")
    
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

    def testCopy(self):
        util.check_dir(config.tmp_dir())
        self.spec.read("samples/popt/popt.pspec")
        self.spec.write(os.path.join(config.tmp_dir(), 'popt-copy.pspec'))

suite = unittest.makeSuite(SpecFileTestCase)

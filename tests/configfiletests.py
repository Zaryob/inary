
import unittest
import os

from pisi.configfile import ConfigurationFile

class ConfigFileTestCase(unittest.TestCase):

    def setUp(self):
        self.cf = ConfigurationFile("tests/pisi.conf")

    def testSections(self):
        cf = self.cf
        if not cf.general:
            self.fail("No 'general' section found in ConfigurationFile")
        if not cf.build:
            self.fail("No 'build' section found in ConfigurationFile")
        if not cf.dirs:
            self.fail("No 'dirs' section found in ConfigurationFile")

    def testValues(self):
        cf = self.cf

        # test values from pisi.conf file
        self.assertEqual(cf.general.destinationdirectory, "/testing")
        self.assertEqual(cf.dirs.archives_dir, "/disk2/pisi/archives")

        # test default values
        self.assertEqual(cf.dirs.tmp_dir, "/var/tmp/pisi")

    def testAccessMethods(self):
        cf = self.cf

        self.assertEqual(cf.build.host, cf.build["host"])
        self.assertEqual(cf.dirs.index_dir, cf.dirs["index_dir"])

suite = unittest.makeSuite(ConfigFileTestCase)

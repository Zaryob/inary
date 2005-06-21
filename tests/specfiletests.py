
import unittest

from pisi import specfile

class SpecReadTestCase(unittest.TestCase):
    def setUp(self):
	self.spec = specfile.SpecFile()
	self.spec.read("samples/popt/popt.pspec")
	
    def testSourceName(self):
	self.assertEqual(self.spec.source.name,
			    "popt")

    def testSourceVersion(self):
	self.assertEqual(self.spec.source.version,
			 "1.7")

    def testSourceLastRelease(self):
	self.assertEqual(self.spec.source.release,
			 "3")

    def testSHA1Sum(self):
	self.assertEqual(self.spec.source.archiveSHA1,
			    "66f3c77b87a160951b180447f4a6dce68ad2f71b")

    def testLenPackages(self):
	self.assertEqual(len(self.spec.packages), 1)


suite = unittest.makeSuite(SpecReadTestCase)

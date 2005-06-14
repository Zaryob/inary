
import unittest

from pisi import specfile

class SpecReadTestCase(unittest.TestCase):
    def setUp(self):
	self.spec = specfile.SpecFile()
	self.spec.read("samples/popt.pspec")
	
    def testSourceName(self):
	self.assertEqual(self.spec.source.name,
			    "popt")

    def testSourceVersion(self):
	self.assertEqual(self.spec.source.version,
			 "1.7")

    def testSourceLastRelease(self):
	self.assertEqual(self.spec.source.release,
			 "3")

    def testMD5Sum(self):
	self.assertEqual(self.spec.source.archiveMD5,
			    "5988e7aeb0ae4dac8d83561265984cc9")

    def testLenPackages(self):
	self.assertEqual(len(self.spec.packages), 1)


suite = unittest.makeSuite(SpecReadTestCase)

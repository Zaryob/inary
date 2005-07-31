
import unittest
import os

from pisi.installdb import installdb
from pisi import util
from pisi.config import config

class InstallDBTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def testRemoveDummy(self):
        installdb.remove('installtest')
        self.assert_(not installdb.is_installed('installtest'))
        
    def testInstall(self):
        installdb.purge('installtest')
        installdb.install('installtest', '0.1', '2')

    def testRemovePurge(self):
        installdb.install('installtest', '0.1', '2')
        self.assert_(installdb.is_installed('installtest'))
        installdb.remove('installtest')
        self.assert_(installdb.is_removed('installtest'))
        installdb.purge('installtest')
        self.assert_(not installdb.is_recorded('installtest'))

suite = unittest.makeSuite(InstallDBTestCase)


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
        installdb.install('installtest', '0.1', '2', './tests/sandbox/files.xml')
        f = installdb.files('installtest')
        a = f.readlines()
        self.assertEqual(a[0], 'placeholder\n')
        self.assert_(installdb.is_installed('installtest'))

    def testRemovePurge(self):
        installdb.install('installtest', '0.1', '2', './tests/sandbox/files.xml')
        self.assert_(installdb.is_installed('installtest'))
        installdb.remove('installtest')
        self.assert_(installdb.is_removed('installtest'))
        installdb.purge('installtest')
        self.assert_(not installdb.is_recorded('installtest'))
        self.assert_(not os.access(installdb.files_name('installtest', '0.1','2'), os.F_OK))

suite = unittest.makeSuite(InstallDBTestCase)


import unittest
import os

from pisi import installdb
from pisi import util
from pisi import context

class InstallDBTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = context.Context()
        pass

    def testRemoveDummy(self):
        installdb.remove('installtest', '0.1', '2')
        self.assert_(not installdb.is_installed('installtest', '0.1', '2'))
        
    def testInstall(self):
        installdb.remove('installtest', '0.1', '2')
        installdb.install('installtest', '0.1', '2', './unittests/sandbox/files.xml')
        f = installdb.files('installtest', '0.1', '2')
        a = f.readlines()
        self.assertEqual(a[0], 'placeholder\n')
        self.assert_(installdb.is_installed('installtest', '0.1', '2'))

    def testRemovePurge(self):
        installdb.install('installtest', '0.1', '2', './unittests/sandbox/files.xml')
        self.assert_(installdb.is_installed('installtest', '0.1', '2'))
        installdb.remove('installtest', '0.1', '2')
        self.assert_(installdb.is_removed('installtest', '0.1', '2'))
        installdb.purge('installtest', '0.1', '2')
        self.assert_(not installdb.is_recorded('installtest', '0.1', '2'))
        self.assert_(not os.access(installdb.files_name('installtest', '0.1', '2'), os.F_OK))

suite = unittest.makeSuite(InstallDBTestCase)

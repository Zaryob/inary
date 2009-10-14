import unittest
import pisi.files

class FilesTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testFileInfo(self):
        file1 = pisi.files.FileInfo(path = '/usr/bin/acpi')
        file1.type = 'init'
        file1.size = '30'

        file2 = pisi.files.FileInfo(path = '/sbin/blkid', type = 'ctors', size = '8')

    def testFiles(self):
        self.files = pisi.files.Files()
        self.files.read('repos/pardus-2007/system/base/curl/pspec.xml')


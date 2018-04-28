import unittest
import inary.data.files

class FilesTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testFileInfo(self):
        file1 = inary.data.files.FileInfo(path = '/usr/bin/acpi')
        file1.type = 'init'
        file1.size = '30'

        file2 = inary.data.files.FileInfo(path = '/sbin/blkid', type = 'ctors', size = '8')

    def testFiles(self):
        self.files = inary.data.files.Files()
        self.files.read('repos/repo1/system/base/bash/pspec.xml')


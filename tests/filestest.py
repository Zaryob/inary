import unittest
import inary.files

class FilesTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testFileInfo(self):
        file1 = inary.files.FileInfo(path = '/usr/bin/acpi')
        file1.type = 'init'
        file1.size = '30'

        file2 = inary.files.FileInfo(path = '/sbin/blkid', type = 'ctors', size = '8')

    def testFiles(self):
        self.files = inary.files.Files()
        self.files.read('repos/pardus-2007/system/base/curl/pspec.xml')


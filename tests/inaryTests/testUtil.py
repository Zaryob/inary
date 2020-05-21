import unittest
import shutil
from inary.util import *
import os


class UtilTestCase(unittest.TestCase):

    def initialize(self):
        testcase.testCase.initialize(self, database=False)

    # process related functions
    def testRunBatch(self):
        self.assertEqual((0, '', b''), run_batch('cd'))
        self.assertEqual(
            (127, '', b'/bin/sh: add: command not found\n'), run_batch('add'))

    def testRunLogged(self):
        assert 0 == run_logged('ls')
        assert 1 == run_logged('rm')

    def testXtermTitle(self):
        xterm_title('sulin')
        xterm_title_reset()

    # path processing functions tests
    def testSplitPath(self):
        assert ['usr', 'local', 'src'] == splitpath('usr/local/src')
        assert ['usr', 'lib', 'sulin'] == splitpath('usr/lib/sulin')

    def testSubPath(self):
        self.assertTrue(subpath('usr', 'usr'))
        self.assertTrue(subpath('usr', 'usr/local/src'))
        self.assertTrue(not subpath('usr/local', 'usr'))

    def testRemovePathPrefix(self):
        pathname = removepathprefix('usr/local', 'usr/local/src')
        assert 'src' == pathname

        pathname = removepathprefix('usr/local', 'usr/local/bin')
        assert not 'bim' == pathname

    def testJoinPath(self):
        assert 'usr/local/src' == join_path('usr/local', 'src')
        assert not 'usr/lib/hal' == join_path('usr', 'hal')
        assert 'usr/sbin/lpc' == join_path('usr', 'sbin/lpc')

    # file/directory related functions tests
    def testCheckFile(self):
        assert check_file('/usr/bin/bash')
        try:
            check_file('/usr/bin/aatests')
        except BaseException:
            assert True

    def testCleanDir(self):
        assert None is clean_dir('usr/lib')
        assert None is clean_dir('usr/local')
        assert not 'tmp/inary-root' == clean_dir('usr/tmp')

    def testDirSize(self):
        self.assertNotEqual(dir_size('usr/lib/sulin'), 2940)
        self.assertNotEqual(dir_size('usr/lib'), 65)

    def testCopyFile(self):
        copy_file('/etc/inary/inary.conf', '/tmp/inary-test1')
        copy_file('/etc/inary/mirrors.conf', '/tmp/inary-test2')
        copy_file_stat('/etc/inary/inary.conf', '/tmp/inary-test1')

import unittest
import inary
import inary.actionsapi
import os
import shutil


class ShellTestCase(unittest.TestCase):
    def setUp(self):
        from inary.actionsapi.variables import initVariables
        unittest.TestCase.setUp(self)
        initVariables()
        return

    def testCanAccessFile(self):
        from inary.actionsapi.shelltools import can_access_file
        self.assertTrue(can_access_file(__file__))
        self.assertFalse(can_access_file('actionsapi/set.py'))

    def testCanAccessDirectory(self):
        from inary.actionsapi.shelltools import can_access_directory
        self.assertTrue(can_access_directory('tests/'))
        self.assertFalse(can_access_directory('tests/mirrors.conf'))

    def testMakedirs(self):
        from inary.actionsapi.shelltools import makedirs

        makedirs('tests/testdirectory/aDirectory')
        self.assertEqual(os.path.exists(
            'tests/testdirectory/aDirectory'), True)
        shutil.rmtree('tests/testdirectory')

    def testEcho(self):
        from inary.actionsapi.shelltools import echo

        echo('tests/echo-file', 'eco subject')
        self.assertEqual(os.path.exists('tests/echo-file'), True)
        self.assertEqual(open('tests/echo-file').readlines()
                         [0].strip(), 'eco subject')
        echo('tests/echo-file', 'subject eco')
        self.assertEqual(open('tests/echo-file').readlines()
                         [1].strip(), 'subject eco')
        os.remove('tests/echo-file')

    def testSym(self):
        from inary.actionsapi.shelltools import sym

        sym('../../scenarios/repo', 'tests/repos')
        self.assertEqual(os.path.islink('tools'), False)
        self.assertEqual(os.path.islink('tests/repos'), True)

    def testUnlinkDir(self):
        from inary.actionsapi.shelltools import makedirs
        from inary.actionsapi.shelltools import sym
        from inary.actionsapi.shelltools import unlinkDir

        makedirs('tests/testdirectory/sample')
        sym('testdirectory/sample', 'tests/history')
        self.assertEqual(os.path.islink('tests/history'), True)
        unlinkDir('tests/testdirectory/sample')
        self.assertEqual(os.path.islink('tests/testdirectory/sample'), False)

    def testCopy(self):
        from inary.actionsapi.shelltools import echo
        from inary.actionsapi.shelltools import copy
        from inary.actionsapi.shelltools import makedirs

        makedirs('tests/testdirectory/sample')
        copy('tests', 'tests-copy')
        self.assertEqual(os.path.islink('tests-copy'), False)
        shutil.rmtree("tests-copy")

        echo('tests/echo-file', 'subject eco')
        copy('tests/echo-file', 'tests/echo-file-copy')
        self.assertEqual(os.path.islink('tests/echo-file-copy'), False)
        os.remove("tests/echo-file")

    def testIsLink(self):
        from inary.actionsapi.shelltools import sym
        from inary.actionsapi.shelltools import isLink

        sym('../database', 'tests/history')
        assert isLink('tests/history')
        assert not isLink('tests/runtests.py')

    def testIsFile(self):
        from inary.actionsapi.shelltools import isFile

        assert isFile('/bin/bash')
        assert not isFile('/tests/database')

    def testIsDirectory(self):
        from inary.actionsapi.shelltools import isDirectory

        assert not isDirectory('doc/dependency.pdf')
        assert isDirectory('/usr/lib')
        assert isDirectory('/etc/inary')
        assert not isDirectory('tests/shelltest.py')

    def testRealPath(self):
        from inary.actionsapi.shelltools import realPath

        assert realPath('doc/dependency.pdf')
        assert realPath('tests/database/sourcedbtest.py')

    def testBaseName(self):
        from inary.actionsapi.shelltools import baseName

        assert 'dependency.pdf' == baseName('doc/dependency.pdf')
        assert 'Arphic' == baseName('licenses/Arphic')
        assert not 'Atmel' == baseName('tools/atmel.py')

    def testSystem(self):
        from inary.actionsapi.shelltools import system

        self.assertEqual(os.path.exists('tests/systemtest'), False)
        system('touch tests/systemtest')
        self.assertEqual(os.path.exists('tests/systemtest'), True)
        os.remove('tests/systemtest')

import unittest
import pisi
import pisi.actionsapi
import os
import shutil

class ShellTestCase(unittest.TestCase):
    def setUp(self):
        from pisi.actionsapi.variables import initVariables
        unittest.TestCase.setUp(self)
        initVariables()
        return

    def testCanAccessFile(self):
        from pisi.actionsapi.shelltools import can_access_file
        assert can_access_file('/usr/lib/engines/libaep.so')
        assert not can_access_file('actionsapi/set.py')

    def testCanAccessDirectory(self):
        from pisi.actionsapi.shelltools import can_access_directory
        assert can_access_directory('/boot')
        assert can_access_directory('/usr/bin')
        assert not can_access_directory('/tests/mirrors.conf')

    def testMakedirs(self):
        from pisi.actionsapi.shelltools import makedirs

        makedirs('tests/testdirectory/aDirectory')
        self.assertEqual(os.path.exists('tests/testdirectory/aDirectory'),True)
        shutil.rmtree('tests/testdirectory')

    def testEcho(self):
        from pisi.actionsapi.shelltools import echo

        echo('tests/echo-file','eco subject')
        self.assertEqual(os.path.exists('tests/echo-file'),True)
        self.assertEqual(open('tests/echo-file').readlines()[0].strip(), 'eco subject')
        echo('tests/echo-file', 'subject eco')
        self.assertEqual(open('tests/echo-file').readlines()[1].strip(), 'subject eco')
        os.remove('tests/echo-file')

    def testSym(self):
        from pisi.actionsapi.shelltools import sym

        sym('scenarios/repo','tests/repos')
        self.assertEqual(os.path.islink('tools'),False)
        self.assertEqual(os.path.islink('tests/repos'),True)

    def testUnlinkDir(self):
        from pisi.actionsapi.shelltools import makedirs
        from pisi.actionsapi.shelltools import sym
        from pisi.actionsapi.shelltools import unlinkDir

        makedirs('tests/testdirectory/sample')
        sym('tests/testdirectory/sample','tests/history')
        self.assertEqual(os.path.islink('tests/history'),True)
        unlinkDir('tests/testdirectory/sample')
        self.assertEqual(os.path.islink('tests/testdirectory/sample'),False)

    def testCopy(self):
        from pisi.actionsapi.shelltools import copy

        copy('/pisi/tests', '/pisi/tests-copy')
        self.assertEqual(os.path.islink('pisi/tests-copy'),False)

        copy('pisi/tests/scripts/sync-licenses', 'pisi/tests/scripts/sync-licenses-copy')
        self.assertEqual(os.path.islink('pisi/tests/scripts/sync-licenses-copy'),False)

    def testIsLink(self):
        from pisi.actionsapi.shelltools import sym
        from pisi.actionsapi.shelltools import isLink

        sym('tests/database','tests/history')
        assert isLink('tests/history')
        assert not isLink('tests/runtests.py')

    def testIsFile(self):
        from pisi.actionsapi.shelltools import isFile

        assert isFile('/usr/lib/engines/libaep.so')
        assert not isFile('/tests/database')

    def testIsDirectory(self):
        from pisi.actionsapi.shelltools import isDirectory

        assert not isDirectory('doc/dependency.pdf')
        assert isDirectory('/usr/lib')
        assert isDirectory('/etc/pisi')
        assert not isDirectory('/tests/shelltest.py')

    def testRealPath(self):
        from pisi.actionsapi.shelltools import realPath

        assert realPath('doc/dependency.pdf')
        assert realPath('tests/database/sourcedbtest.py')

    def testBaseName(self):
        from pisi.actionsapi.shelltools import baseName

        assert 'dependency.pdf' == baseName('doc/dependency.pdf')
        assert 'Arphic' == baseName('licenses/Arphic')
        assert not 'Atmel' == baseName('tools/atmel.py')

    def testSystem(self):
        from pisi.actionsapi.shelltools import system

        self.assertEqual(os.path.exists('tests/systemtest'),False)
        system('touch tests/systemtest')
        self.assertEqual(os.path.exists('tests/systemtest'),True)
        os.remove('tests/systemtest')

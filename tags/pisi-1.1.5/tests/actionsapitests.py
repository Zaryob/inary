# -*- coding: utf-8 -*-
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import unittest
import zipfile
import shutil
import os
import pwd
import grp
import time

import testcase

class ActionsAPITestCase(testcase.TestCase):
    def setUp(self):
        from pisi.actionsapi.variables import initVariables

        testcase.TestCase.setUp(self)
        initVariables()
        #FIXME: test incomplete
        return
        self.f = zipfile.ZipFile("helloworld-0.1-1.pisi", "r")
        self.filelist = []

        for file in self.f.namelist():
            self.filelist.append(file)

    def testFileList(self):
        #FIXME: test incomplete
        return
        fileContent = ["files.xml", \
                       "install/bin/helloworld", \
                       "install/opt/PARDUS", \
                       "install/opt/helloworld/helloworld", \
                       "install/opt/uludag", \
                       "install/sbin/helloworld", \
                       "install/sys/PARDUS", \
                       "install/sys/uludag", \
                       "install/usr/bin/goodbye", \
                       "install/usr/bin/helloworld", \
                       "install/usr/lib/helloworld.o", \
                       "install/usr/sbin/goodbye", \
                       "install/usr/sbin/helloworld", \
                       "install/usr/share/doc/helloworld-0.1-1/Makefile.am", \
                       "install/usr/share/doc/helloworld-0.1-1/goodbyeworld.cpp", \
                       "install/usr/share/info/Makefile.am", \
                       "install/usr/share/info/Makefile.cvs", \
                       "install/usr/share/info/Makefile.in", \
                       "install/var/goodbye", \
                       "install/var/hello", \
                       "metadata.xml"]

        '''check number of files in package'''
        self.assertEqual(fileContent.__len__(), self.filelist.__len__())

        '''check file content'''
        for file in self.filelist:
            self.assert_(fileContent.__contains__(file))

    def testShelltoolsCanAccessFile(self):
        from pisi.actionsapi.shelltools import can_access_file

        self.assert_(can_access_file('tests/actionsapitests/file'))
        self.assert_(not can_access_file('tests/actionsapitests/fileX'))
        self.assert_(can_access_file('tests/actionsapitests/linktoafile'))

    def testShelltoolsCanAccessDir(self):
        from pisi.actionsapi.shelltools import can_access_directory

        self.assert_(can_access_directory('tests/actionsapitests/adirectory'))
        self.assert_(not can_access_directory('tests/actionsapitests/adirectoryX'))
        self.assert_(can_access_directory('tests/actionsapitests/linktoadirectory'))

    def testShelltoolsMakedirs(self):
        from pisi.actionsapi.shelltools import makedirs

        makedirs('tests/actionsapitests/testdirectory/into/a/directory')
        self.assertEqual(os.path.exists('tests/actionsapitests/testdirectory/into/a/directory'), True)
        shutil.rmtree('tests/actionsapitests/testdirectory')

    def testShelltoolsEcho(self):
        from pisi.actionsapi.shelltools import echo

        echo('tests/actionsapitests/echo-file', 'hububat fiyatları')
        self.assertEqual(os.path.exists('tests/actionsapitests/echo-file'), True)
        self.assertEqual(open('tests/actionsapitests/echo-file').readlines()[0].strip(), "hububat fiyatları")
        echo('tests/actionsapitests/echo-file', 'fiyat hububatları')
        self.assertEqual(open('tests/actionsapitests/echo-file').readlines()[1].strip(), "fiyat hububatları")
        os.remove('tests/actionsapitests/echo-file')

    def testShelltoolsChmod(self):
        from pisi.actionsapi.shelltools import chmod

        chmod('tests/actionsapitests/file')
        self.assertEqual(oct(os.stat('tests/actionsapitests/file').st_mode)[-3:], '755')
        chmod('tests/actionsapitests/file', 0644)
        self.assertEqual(oct(os.stat('tests/actionsapitests/file').st_mode)[-3:], '644')

    def testShelltoolsChown(self):
        from pisi.actionsapi.shelltools import chown

        f = open('tests/actionsapitests/chowntest', 'w')
        f.close()
        chown('tests/actionsapitests/chowntest')
        self.assertEqual(os.stat('tests/actionsapitests/chowntest').st_uid, pwd.getpwnam('root')[2])
        self.assertEqual(os.stat('tests/actionsapitests/chowntest').st_gid, grp.getgrnam('root')[2])
        chown('tests/actionsapitests/chowntest', 'daemon', 'wheel')
        self.assertEqual(os.stat('tests/actionsapitests/chowntest').st_uid, pwd.getpwnam('daemon')[2])
        self.assertEqual(os.stat('tests/actionsapitests/chowntest').st_gid, grp.getgrnam('wheel')[2])
        os.remove('tests/actionsapitests/chowntest')

    def testShelltoolsSym(self):
        from pisi.actionsapi.shelltools import sym

        sym('tests/actionsapitests/file', 'tests/actionsapitests/filelnk')
        self.assert_(os.path.islink('tests/actionsapitests/filelnk'))
        self.assertEqual(os.readlink('tests/actionsapitests/filelnk'), 'tests/actionsapitests/file')
        os.remove('tests/actionsapitests/filelnk')

    def testShelltoolsUnlink(self):
        from pisi.actionsapi.shelltools import unlink

        f = open('tests/actionsapitests/unlinktest', 'w')
        f.close()
        os.symlink('tests/actionsapitests/unlinktest', 'tests/actionsapitests/unlinktest-sym')
        unlink('tests/actionsapitests/unlinktest')
        self.assert_(not os.path.exists('tests/actionsapitests/unlinktest'))

        unlink('tests/actionsapitests/unlinktest-sym')
        self.assert_(not os.path.exists('tests/actionsapitests/unlinktest-sym'))

    def testShelltoolsUnlinkDir(self):
        from pisi.actionsapi.shelltools import unlinkDir

        os.mkdir('tests/actionsapitests/unlinkdir')
        f = open('tests/actionsapitests/unlinkdir/unlinktest', 'w')
        f.close()

        #FIXME: unlinkDir cannot unlink a link to a directory.
        #Instead it deletes content of linked directory, then leaves directory and link
        #unlinkDir('tests/actionsapitests/linktoadirectory')
        #self.assert_(not os.path.exists('tests/actionsapitests/linktoadirectory'))
        #os.symlink('tests/actionsapitests/linkeddir', 'tests/actionsapitests/linktoadirectory')

        unlinkDir('tests/actionsapitests/unlinkdir')
        self.assert_(not os.path.exists('tests/actionsapitests/unlinkdir'))

    def testShelltoolsMove(self):
        from pisi.actionsapi.shelltools import move

        move('tests/actionsapitests/brokenlink', 'tests/actionsapitests/brokenlink-move')
        self.assert_(os.path.islink('tests/actionsapitests/brokenlink-move'))
        self.assertEqual(os.readlink('tests/actionsapitests/brokenlink-move'), '/no/such/place')
        self.assert_(not os.path.exists('tests/actionsapitests/brokenlink'))
        shutil.move('tests/actionsapitests/brokenlink-move', 'tests/actionsapitests/brokenlink')

        move('tests/actionsapitests/brokenlink', 'tests/actionsapitests/adirectory/brokenlink-move')
        self.assert_(os.path.islink('tests/actionsapitests/adirectory/brokenlink-move'))
        self.assertEqual(os.readlink('tests/actionsapitests/adirectory/brokenlink-move'), '/no/such/place')
        self.assert_(not os.path.exists('tests/actionsapitests/brokenlink'))
        shutil.move('tests/actionsapitests/adirectory/brokenlink-move', 'tests/actionsapitests/brokenlink')

        move('tests/actionsapitests/file', 'tests/actionsapitests/adirectory')
        self.assert_(os.path.isfile('tests/actionsapitests/adirectory/file'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/file'), 321)
        self.assert_(not os.path.exists('tests/actionsapitests/file'))
        shutil.move('tests/actionsapitests/adirectory/file', 'tests/actionsapitests/')

        move('tests/actionsapitests/file', 'tests/actionsapitests/file-move')
        self.assert_(os.path.isfile('tests/actionsapitests/file-move'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/file-move'), 321)
        self.assert_(not os.path.exists('tests/actionsapitests/file'))
        shutil.move('tests/actionsapitests/file-move', 'tests/actionsapitests/file')

        move('tests/actionsapitests/file', 'tests/actionsapitests/adirectory/filewithanothername')
        self.assert_(os.path.exists('tests/actionsapitests/adirectory/filewithanothername'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/filewithanothername'), 321)
        self.assert_(not os.path.exists('tests/actionsapitests/file'))
        shutil.move('tests/actionsapitests/adirectory/filewithanothername', 'tests/actionsapitests/file')

        #FIXME: this type of moving (without changing name) doesn't work
        #And I'm not sure the right way is to use 'tests/actionsapitests/adirectory/linkeddir' as dest.
        #move('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory')
        #self.assert_(os.path.exists('tests/actionsapitests/adirectory/linkeddir/file'))
        #self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/linkeddir/file'), 321)
        #shutil.move('tests/actionsapitests/adirectory/linkeddir', 'tests/actionsapitests/linkeddir')

        move('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory/withanothername')
        self.assert_(os.path.exists('tests/actionsapitests/adirectory/withanothername/file'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/withanothername/file'), 321)
        shutil.move('tests/actionsapitests/adirectory/withanothername', 'tests/actionsapitests/linkeddir')

    def testShelltoolsCopy(self):
        from pisi.actionsapi.shelltools import copy

        copy('tests/actionsapitests/brokenlink', 'tests/actionsapitests/brokenlink-copy')
        self.assertEqual(os.path.islink('tests/actionsapitests/brokenlink-copy'), True)
        os.remove('tests/actionsapitests/brokenlink-copy')

        copy('tests/actionsapitests/brokenlink', 'tests/actionsapitests/adirectory')
        self.assertEqual(os.path.islink('tests/actionsapitests/adirectory/brokenlink'), True)

        copy('tests/actionsapitests/brokenlink', 'tests/actionsapitests/adirectory/brknlnk')
        self.assertEqual(os.path.islink('tests/actionsapitests/adirectory/brknlnk'), True)
        os.remove('tests/actionsapitests/adirectory/brknlnk')

        self.assertEqual(os.readlink('tests/actionsapitests/adirectory/brokenlink'), '/no/such/place')
        os.remove('tests/actionsapitests/adirectory/brokenlink')

        copy('tests/actionsapitests/linktoadirectory', 'tests/actionsapitests/adirectory/', False)
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/linktoadirectory/file'), True)
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/linktoadirectory/file'), 321)
        shutil.rmtree('tests/actionsapitests/adirectory/linktoadirectory')

        copy('tests/actionsapitests/file', 'tests/actionsapitests/adirectory')
        self.assertEqual(os.path.isfile('tests/actionsapitests/adirectory/file'), True)
        #overwrite..
        copy('tests/actionsapitests/file', 'tests/actionsapitests/adirectory')
        os.remove('tests/actionsapitests/adirectory/file')

        copy('tests/actionsapitests/linktoafile', 'tests/actionsapitests/adirectory', False)
        ourguy = 'tests/actionsapitests/%s' % os.readlink('tests/actionsapitests/linktoafile')
        self.assert_(os.path.exists(ourguy))

        copy('tests/actionsapitests/file', 'tests/actionsapitests/file-copy')
        self.assertEqual(os.path.exists('tests/actionsapitests/file-copy'), True)
        os.remove('tests/actionsapitests/file-copy')

        copy('tests/actionsapitests/file', 'tests/actionsapitests/adirectory/filewithanothername')
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/filewithanothername'), True)
        os.remove('tests/actionsapitests/adirectory/filewithanothername')

        copy('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory')
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/linkeddir/file'), True)
        shutil.rmtree('tests/actionsapitests/adirectory/linkeddir')

        copy('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory/withanothername')
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/withanothername/file'), True)
        shutil.rmtree('tests/actionsapitests/adirectory/withanothername')

    def testShelltoolsCopyTree(self):
        from pisi.actionsapi.shelltools import copytree

        copytree('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory')
        self.assert_(os.path.exists('tests/actionsapitests/linkeddir/file'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/linkeddir/file'), 321)
        self.assert_(os.path.exists('tests/actionsapitests/adirectory/linkeddir/file'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/linkeddir/file'), 321)
        shutil.rmtree('tests/actionsapitests/adirectory/linkeddir')

        copytree('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory/withanothername')
        self.assert_(os.path.exists('tests/actionsapitests/linkeddir/file'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/linkeddir/file'), 321)
        self.assert_(os.path.exists('tests/actionsapitests/adirectory/withanothername/file'))
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/withanothername/file'), 321)
        shutil.rmtree('tests/actionsapitests/adirectory/withanothername')

    def testShelltoolsTouch(self):
        from pisi.actionsapi.shelltools import touch

        touch('tests/actionsapitests/file-touch')
        self.assert_(os.path.exists('tests/actionsapitests/file-touch'))
        os.remove('tests/actionsapitests/file-touch')

        atime = int(time.time())
        touch('tests/actionsapitests/file')
        self.assertEqual(os.path.getsize('tests/actionsapitests/file'), 321)
        self.assert_(atime <= os.stat('tests/actionsapitests/file').st_atime)

    def testShelltoolsCd(self):
        from pisi.actionsapi.shelltools import cd

        current = os.getcwd()
        cd('tests/actionsapitests')
        self.assertEqual(os.path.getsize('file'), 321)
        cd()
        self.assertEqual(os.path.getsize('actionsapitests/file'), 321)
        os.chdir(current)

    def testShelltoolsLs(self):
        from pisi.actionsapi.shelltools import ls

        self.assertEqual(os.listdir('tests/actionsapitests'), ls('tests/actionsapitests'))

        self.assertEqual(os.listdir('tests/actionsapitests/linkeddir'), ls('tests/actionsapitests/linktoadirectory'))

        self.assertEqual(['tests/actionsapitests/file'], ls('tests/actionsapitests/f*'))

    def testShelltoolsExport(self):
        from pisi.actionsapi.shelltools import export

        export('hububat', 'fiyatları')
        self.assertEqual(os.environ['hububat'], 'fiyatları')
        del(os.environ['hububat'])

    def testShelltoolsIsLink(self):
        from pisi.actionsapi.shelltools import isLink

        self.assert_(isLink('tests/actionsapitests/linktoadirectory'))
        self.assert_(isLink('tests/actionsapitests/linktoafile'))
        self.assert_(isLink('tests/actionsapitests/brokenlink'))
        self.assert_(not isLink('tests/actionsapitests/file'))
        self.assert_(not isLink('tests/actionsapitests/adirectory'))

    def testShelltoolsIsFile(self):
        from pisi.actionsapi.shelltools import isFile

        self.assert_(not isFile('tests/actionsapitests/linktoadirectory'))
        self.assert_(not isFile('tests/actionsapitests/linktoafile'))
        self.assert_(not isFile('tests/actionsapitests/brokenlink'))
        self.assert_(isFile('tests/actionsapitests/file'))
        self.assert_(not isFile('tests/actionsapitests/adirectory'))

    def testShelltoolsIsDirectory(self):
        from pisi.actionsapi.shelltools import isDirectory

        self.assert_(not isDirectory('tests/actionsapitests/linktoadirectory'))
        self.assert_(not isDirectory('tests/actionsapitests/linktoafile'))
        self.assert_(not isDirectory('tests/actionsapitests/brokenlink'))
        self.assert_(not isDirectory('tests/actionsapitests/file'))
        self.assert_(isDirectory('tests/actionsapitests/adirectory'))

    def testShelltoolsSystem(self):
        from pisi.actionsapi.shelltools import system as s

        self.assertEqual(os.path.exists('tests/actionsapitests/systest'), False)
        s('touch tests/actionsapitests/systest')
        self.assertEqual(os.path.exists('tests/actionsapitests/systest'), True)
        os.remove('tests/actionsapitests/systest')

suite = unittest.makeSuite(ActionsAPITestCase)

# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import unittest
import zipfile

import testcase

class ActionsAPITestCase(testcase.TestCase):
    def setUp(self):
        testcase.TestCase.setUp(self)
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

suite = unittest.makeSuite(ActionsAPITestCase)

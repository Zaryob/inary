# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import os
from os.path import exists as pathexists
from os.path import basename, islink, join

import pisi.context as ctx
import pisi.api
from pisi import archive
from pisi import sourcearchive
from pisi import fetcher
from pisi import util
from pisi.build import BuildContext
from pisi import uri 

import testcase

class ArchiveFileTestCase(testcase.TestCase):

    def testUnpackTar(self):
        bctx = BuildContext("tests/popt/pspec.xml")

        achv = sourcearchive.SourceArchive(bctx)
    
        assert bctx.spec.source.archiveType == "targz"

        # skip fetching and directly unpack the previously fetched (by
        # fetchertests) archive
        if not achv.is_cached(interactive=False):
            achv.fetch(interactive=False)
        achv.unpack()
    
        targetDir = bctx.pkg_work_dir()
        # but testing is hard
        # "var/tmp/pisi/popt-1.7-3/work" (targetDir)
        assert pathexists(targetDir + "/popt-1.7")

        testfile = targetDir + "/popt-1.7/Makefile.am"
        assert pathexists(testfile)
    
        # check file integrity
        self.assertEqual(util.sha1_file(testfile),
             "5af9dd7d754f788cf511c57ce0af3d555fed009d")

    def testUnpackZip(self):
        bctx = BuildContext("tests/pccts/pspec.xml")

        assert bctx.spec.source.archiveType == "zip"

        achv = sourcearchive.SourceArchive(bctx)
        achv.fetch(interactive=False)
        achv.unpack(cleanDir=True)

        targetDir = bctx.pkg_work_dir()
        assert pathexists(targetDir + "/pccts")

        testfile = targetDir + "/pccts/history.txt"
        assert pathexists(testfile)
    
        # check file integrity
        self.assertEqual(util.sha1_file(testfile),
             "f2be0f9783e84e98fe4e2b8201a8f506fcc07a4d")

# TODO: no link file in pccts package. Need to find a ZIP file
# containing a symlink
        # check for symbolic links
#        testfile = targetDir + "/sandbox/testdir/link1"
#        assert islink(testfile)

    def testMakeZip(self):
        # first unpack our dear sandbox.zip
        bctx = BuildContext("tests/pccts/pspec.xml")
        targetDir = bctx.pkg_work_dir()
        achv = sourcearchive.SourceArchive(bctx)
        achv.fetch(interactive=False)
        achv.unpack(cleanDir=True)
        del achv

        newZip = targetDir + "/new.zip"
        zip = archive.ArchiveZip(newZip, 'zip', 'w')
        sourceDir = targetDir + "/pccts"
        zip.add_to_archive(sourceDir)
        zip.close()

        #TODO: do some more work to test the integrity of new zip file
    
    def testUnpackZipCond(self):
        bctx = BuildContext("tests/pccts/pspec.xml")
        url = uri.URI(bctx.spec.source.archiveUri)
        targetDir = bctx.pkg_work_dir()
        filePath = join(ctx.config.archives_dir(), url.filename())

        # check cached
        if util.sha1_file(filePath) != bctx.spec.source.archiveSHA1:
            fetch = fetcher.Fetcher(bctx.spec.source.archiveUri, targetDir)
            fetch.fetch()
        assert bctx.spec.source.archiveType == "zip"

        achv = archive.Archive(filePath, bctx.spec.source.archiveType)
        achv.unpack_files(["pccts/history.txt"], targetDir)
        assert pathexists(targetDir + "/pccts")
        testfile = targetDir + "/pccts/history.txt"
        assert pathexists(testfile)

suite = unittest.makeSuite(ArchiveFileTestCase)

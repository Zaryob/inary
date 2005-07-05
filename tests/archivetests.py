
import unittest
import os
from os.path import exists as pathexists
from os.path import basename, islink, join

from pisi import archive
from pisi import sourcearchive
from pisi import fetcher
from pisi import util
from pisi import context
from pisi import purl

class ArchiveFileTestCase(unittest.TestCase):
#     def setUp(self):
#     pass

    def testUnpackTar(self):
        ctx = context.BuildContext("tests/popt/pspec.xml")

        achv = sourcearchive.SourceArchive(ctx)
    
        assert ctx.spec.source.archiveType == "targz"

        # skip fetching and directly unpack the previously fetched (by
        # fetchertests) archive
        if not achv.isCached(interactive=False):
            achv.fetch(interactive=False)
        achv.unpack()
    
        targetDir = ctx.pkg_work_dir()
        # but testing is hard
        # "var/tmp/pisi/popt-1.7-3/work" (targetDir)
        assert pathexists(targetDir + "/popt-1.7")

        testfile = targetDir + "/popt-1.7/Makefile.am"
        assert pathexists(testfile)
    
        # check file integrity
        self.assertEqual(util.sha1_file(testfile),
             "5af9dd7d754f788cf511c57ce0af3d555fed009d")

    def testUnpackZip(self):
        ctx = context.BuildContext("tests/sandbox/pspec.xml")

        assert ctx.spec.source.archiveType == "zip"

        achv = sourcearchive.SourceArchive(ctx)
        achv.fetch(interactive=False)
        achv.unpack(cleanDir=True)

        targetDir = ctx.pkg_work_dir()
        assert pathexists(targetDir + "/sandbox")

        testfile = targetDir + "/sandbox/borek.cs"
        assert pathexists(testfile)
    
        # check file integrity
        self.assertEqual(util.sha1_file(testfile),
             "06d0ee5ba49eccae6bc20552d55b3ba5ad52995e")

        # check for symbolic links
        testfile = targetDir + "/sandbox/deneme/hed"
        assert islink(testfile)

    def testMakeZip(self):
        # first unpack our dear sandbox.zip
        ctx = context.BuildContext("tests/sandbox/pspec.xml")
        targetDir = ctx.pkg_work_dir()
        achv = sourcearchive.SourceArchive(ctx)
        achv.fetch(interactive=False)
        achv.unpack(cleanDir=True)
        del achv

        newZip = targetDir + "/new.zip"
        zip = archive.ArchiveZip(newZip, 'zip', 'w')
        sourceDir = targetDir + "/sandbox"
        zip.add_to_archive(sourceDir)
        zip.close()

        #TODO: do some more work to test the integrity of new zip file

    
    def testUnpackZipCond(self):
        ctx = context.BuildContext("tests/sandbox/pspec.xml")
        url = purl.PUrl(ctx.spec.source.archiveUri)
        targetDir = ctx.pkg_work_dir()
        filePath = join(ctx.archives_dir(), url.filename())

        # check cached
        if util.sha1_file(filePath) != ctx.spec.source.archiveSHA1:
            fetch = fetcher.Fetcher(ctx.spec.source.archiveUri, targetDir)
            fetch.fetch()
        assert ctx.spec.source.archiveType == "zip"

        achv = archive.Archive(filePath, ctx.spec.source.archiveType)
        achv.unpack_files(["sandbox/borek.cs"], targetDir)
        assert pathexists(targetDir + "/sandbox")
        testfile = targetDir + "/sandbox/borek.cs"
        assert pathexists(testfile)

suite = unittest.makeSuite(ArchiveFileTestCase)

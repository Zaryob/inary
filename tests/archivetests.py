import pisi
import unittest
from pisi import util
from pisi import uri
from pisi import archive
from pisi import sourcearchive
from pisi import fetcher
from pisi.specfile import SpecFile
from os.path import join, exists

class ArchiveTestCase(unittest.TestCase):

    def testTarUnpack(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        archiv = sourcearchive.SourceArchive(spec, targetDir)
        archiv.unpack()
        assert spec.source.archive.type == 'targz'


    def testUnpackTarCond(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp'
        archiv = sourcearchive.SourceArchive(spec, targetDir)
        url = uri.URI(spec.source.archive.uri)
        filePath = join(pisi.context.config.archives_dir(), url.filename())
        if util.sha1_file(filePath) != spec.source.archive.sha1sum:
            fetch = fetcher.Fetcher(spec.source.archive.uri, targetDir)
            fetch.fetch()
        assert spec.source.archive.type == 'targz'

    def testZipUnpack(self):
        spec = SpecFile('repos/pardus-2007/system/base/openssl/pspec.xml')
        targetDir = '/tmp/tests'
        archiv = sourcearchive.SourceArchive(spec, targetDir)
        archiv.fetch()
        archiv.unpack()
        assert not exists(targetDir + '/openssl')

    def testMakeZip(self):
        spec = SpecFile('repos/pardus-2007/system/base/openssl/pspec.xml')
        targetDir = '/tmp/tests'
        archiv = sourcearchive.SourceArchive(spec, targetDir)
        archiv.fetch(interactive = False)
        archiv.unpack(clean_dir = True)
        del archiv

        newDir = targetDir + '/newZip'
        zip = archive.ArchiveZip(newDir, 'zip', 'w')
        sourceDir = '/tmp/pisi-root'
        zip.add_to_archive(sourceDir)
        zip.close()

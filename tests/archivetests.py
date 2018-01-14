import inary
import unittest
from inary import util
from inary import uri
from inary import archive
from inary import sourcearchive
from inary import fetcher
from inary.specfile import SpecFile
from os.path import join, exists

class ArchiveTestCase(unittest.TestCase):

    def testTarUnpack(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp/tests'
        archives = sourcearchive.SourceArchives(spec)
        archives.unpack(targetDir)
        for archive in spec.source.archive:
            assert archive.type == 'targz'


    def testUnpackTarCond(self):
        spec = SpecFile('repos/pardus-2007/system/base/curl/pspec.xml')
        targetDir = '/tmp'
        archives = sourcearchive.SourceArchives(spec)
        for archive in spec.source.archive:
            url = uri.URI(archive.uri)
            filePath = join(inary.context.config.archives_dir(), url.filename())
            if util.sha1_file(filePath) != archive.sha1sum:
                fetch = fetcher.Fetcher(archive.uri, targetDir)
                fetch.fetch()
            assert archive.type == 'targz'

    def testZipUnpack(self):
        spec = SpecFile('repos/pardus-2007/system/base/openssl/pspec.xml')
        targetDir = '/tmp/tests'
        archives = sourcearchive.SourceArchives(spec)
        archives.fetch()
        archives.unpack(targetDir)
        assert not exists(targetDir + '/openssl')

    def testMakeZip(self):
        spec = SpecFile('repos/pardus-2007/system/base/openssl/pspec.xml')
        targetDir = '/tmp/tests'
        archives = sourcearchive.SourceArchives(spec)
        archives.fetch(interactive = False)
        archives.unpack(targetDir, clean_dir=True)
        del archives

        newDir = targetDir + '/newZip'
        zip = archive.ArchiveZip(newDir, 'zip', 'w')
        sourceDir = '/tmp/inary-root'
        zip.add_to_archive(sourceDir)
        zip.close()

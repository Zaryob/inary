import unittest
import os
from inary import uri
from inary.file import File
from inary.data.specfile import SpecFile


class UriTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testSetUri(self):
        self.url = uri.URI()
        self.url.set_uri('uri')
        assert 'uri' == self.url.get_uri()
        self.url.set_uri('urix')
        assert 'urix' == self.url.get_uri()

    def testIsLocalFile(self):
        uri1 = uri.URI()
        assert not uri1.is_local_file()
        uri1.set_uri('/usr/local')
        assert uri1.is_local_file()

    def testIsRemoteFile(self):
        uri2 = uri.URI()
        assert uri2.is_remote_file()
        uri2.set_uri('uri')
        assert not uri2.is_remote_file()

    def testSchemePath(self):
        uri3 = uri.URI()
        uri3.set_uri('/usr/bin')
        self.assertEqual('file', uri3.scheme())
        assert '/usr/bin' == uri3.path()

    def testFileName(self):
        uri4 = uri.URI()
        uri4.set_uri('/usr/share/aclocal')
        assert 'aclocal' == uri4.filename()

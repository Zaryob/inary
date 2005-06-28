# Simplifying working with URLs, PURL module provides common URL
# parsing interface

from urlparse import urlparse
from os.path import basename

class PUrl(object):
    """PUrl class provides a URL parser and simplifies working with
    URLs."""

    def __init__(self, uri=None):
        if uri:
            self.setUri(uri)
        else:
            self.__scheme = None
            self.__location = None
            self.__path = None
            self.__filename = None
            self.__params = None
            self.__query = None
            self.__fragment = None
            self.__uri = None

    def getUri(self):
        if self.__uri:
            return self.__uri

    def setUri(self, uri):
        # (scheme, location, path, params, query, fragment)
        u = urlparse(uri, "file")
        self.__scheme = u[0]
        self.__location = u[1]
        self.__path = u[2]
        self.__filename = basename(self.__path)
        self.__params = u[3]
        self.__query = u[4]
        self.__fragment = u[5]

        self.__uri = uri

    def isLocalFile(self):
        if self.scheme() == "file":
            return True
        else:
            return False

    def isRemoteFile(self):
        return not self.isLocalFile()
        
    def scheme(self):
        return self.__scheme

    def location(self):
        return self.__location

    def path(self):
        return self.__path

    def filename(self):
        return self.__filename

    def params(self):
        return self.__params

    def query(self):
        return self.__query

    def fragment(self):
        return self.__fragment

    uri = property(getUri, setUri)

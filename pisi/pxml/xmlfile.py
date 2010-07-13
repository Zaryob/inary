# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

"""
 XmlFile class further abstracts a dom object using the
 high-level dom functions provided in xmlext module (and sorely lacking
 in xml.dom :( )

 function names are mixedCase for compatibility with minidom,
 an 'old library'

 this implementation uses piksemel
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import piksemel as iks

import pisi
import pisi.file

class Error(pisi.Error):
    pass

class XmlFile(object):
    """A class to help reading and writing an XML file"""

    def __init__(self, tag):
        self.rootTag = tag

    def newDocument(self):
        """clear DOM"""
        self.doc = iks.newDocument(self.rootTag)

    def unlink(self):
        """deallocate DOM structure"""
        del self.doc

    def rootNode(self):
        """returns root document element"""
        return self.doc

    def parsexml(self, xml):
        """parses xml string and returns DOM"""
        try:
            self.doc = iks.parseString(xml)
            return self.doc
        except Exception, e:
            raise Error(_("String '%s' has invalid XML") % (xml))

    def readxml(self, uri, tmpDir='/tmp', sha1sum=False,
                compress=None, sign=None, copylocal = False):

        uri = pisi.file.File.make_uri(uri)

        # workaround for repo index files to fix 
        # rev. 17027 regression (http://liste.pardus.org.tr/gelistirici/2008-February/011133.html)
        compressed = pisi.file.File.is_compressed(str(uri))

        if uri.is_local_file() and not compressed:
            # this is a local file
            localpath = uri.path()
        else:
            # this is a remote file, first download it into tmpDir
            localpath = pisi.file.File.download(uri, tmpDir, sha1sum=sha1sum, 
                                                compress=compress,sign=sign, copylocal=copylocal)

        try:
            self.doc = iks.parse(localpath)
            return self.doc
        except OSError, e:
            raise Error(_("Unable to read file (%s): %s") %(localpath,e))
        except Exception, e:
            raise Error(_("File '%s' has invalid XML") % (localpath) )

    def writexml(self, uri, tmpDir = '/tmp', sha1sum=False, compress=None, sign=None):
        f = pisi.file.File(uri, pisi.file.File.write, sha1sum=sha1sum, compress=compress, sign=sign)
        f.write(self.doc.toPrettyString())
        f.close()

    def writexmlfile(self, f):
        f.write(self.doc.toPrettyString())

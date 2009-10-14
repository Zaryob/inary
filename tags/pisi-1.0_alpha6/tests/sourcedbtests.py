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

import pisi.context as ctx
import pisi.api
import pisi.sourcedb
from pisi import util
from pisi.specfile import SpecFile

class SourceDBTestCase(unittest.TestCase):

    def setUp(self):
        pisi.api.init(comar = False)

        self.sourcedb = pisi.sourcedb.init()
        self.spec = SpecFile()
        self.spec.read("tests/popt/pspec.xml")
        
    def testAdd(self):
        self.sourcedb.add_source(self.spec.source)
        self.assert_(self.sourcedb.has_source("popt"))
    
    def testRemove(self):
        self.testAdd()
        self.sourcedb.remove_source("popt")
        self.assert_(not self.sourcedb.has_source("popt"))

suite = unittest.makeSuite(SourceDBTestCase)

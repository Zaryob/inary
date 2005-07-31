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

from pisi.sourcedb import sourcedb
from pisi import util
from pisi import context

class SourceDBTestCase(unittest.TestCase):

    def setUp(self):
        self.ctx = context.BuildContext("tests/popt/pspec.xml")
        
    def testAdd(self):
        sourcedb.add_source(self.ctx.spec.source)
        self.assert_(sourcedb.has_source("popt"))
    
    def testRemove(self):
        self.testAdd()
        sourcedb.remove_source("popt")
        self.assert_(not sourcedb.has_source("popt"))

suite = unittest.makeSuite(SourceDBTestCase)

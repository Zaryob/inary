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

from pisi import xmlfile
from pisi.config import config
import pisi.util as util
import types

class XmlFileTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def testMetaClass(self):
        class A:
            __metaclass__ = xmlfile.autoxml
            t_Number = [types.IntType, xmlfile.mandatory]

suite = unittest.makeSuite(XmlFileTestCase)

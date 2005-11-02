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
import xml.dom.minidom as mdom
from xml.parsers.expat import ExpatError
import types

import pisi
import pisi.api
from pisi import xmlfile
import pisi.context as ctx
import pisi.util as util
from pisi.xmlext import *

import testcase

class XmlExtTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database=False)

    def testGet(self):
        self.a = mdom.parse('tests/a.xml')
        self.doc = self.a.documentElement
        self.assertEqual(getNodeText(self.doc, 'Number'), '868')
        self.assertEqual(getNodeText(self.doc, 'OtherInfo/BirthDate'), '18071976')
        codeswith = getAllNodes(self.doc, 'OtherInfo/CodesWith/Person')
        self.assertEqual(len(codeswith), 4)
        self.assertEqual(getNodeText(codeswith[2]), 'Caglar')
        
    def testAdd(self):
        impl = mdom.getDOMImplementation()
        a = impl.createDocument(None, 'team', None)
        node = a.documentElement
        addText(node, 'team/coder', 'zibidi1')
        addText(node, 'team/coder', 'zibidi2')
        addText(node, 'team/coder', 'zibidi3')
        reada = getAllNodes(node, 'team/coder')
        self.assertEqual(len(reada), 3)

        pass

suite = unittest.makeSuite(XmlExtTestCase)

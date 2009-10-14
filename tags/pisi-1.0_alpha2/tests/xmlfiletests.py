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
from pisi.config import config
import pisi.util as util
from pisi.xmlext import *

class XmlFileTestCase(unittest.TestCase):

    def setUp(self):
        pisi.api.init(False)
    
    def testMetaClass(self):

        class OtherInfo:
            __metaclass__ = xmlfile.autoxml
            t_BirthDate = [types.StringType, xmlfile.mandatory]
            t_Interest = [types.StringType, xmlfile.optional]
            t_CodesWith = [ [types.StringType], xmlfile.optional, 'Person']
        
        class A:
            __metaclass__ = xmlfile.autoxml
            t_Name = [types.StringType, xmlfile.mandatory]
            t_Number = [types.IntType, xmlfile.optional]
            t_Email = [types.StringType, xmlfile.optional]
            a_href = [types.StringType, xmlfile.mandatory]
            #t_Projects = [ [types.StringType], xmlfile.mandatory, 'Project']
            #t_OtherInfo = [ OtherInfo, xmlfile.optional ]

        a = A()
        self.assertEqual(a.href, None)
        dom = mdom.parse('tests/a.xml')
        node = getNode(dom, 'A')
        self.assert_(len(A.decoders)>0)
        a.decode(node)
        self.assert_(a.href.startswith('http'))
        self.assertEqual(a.number, 868)
        self.assertEqual(a.name, 'Eray Ozkural')
        string = a.format()
        print '*', string
        #self.assert_(string.startswith('Name'))
        xml = xmlfile.XmlFile('A')
        a.encode(xml)
        xml.writexml('/tmp/a.xml')
        print '/tmp/a.xml written'
        return
        xml = xmlfile.XmlFile('A')
        a2 = A()
        a2.name = "Baris Metin"
        a2.email = "baris@uludag.org.tr"
        a2.href = 'http://cekirdek.uludag.org.tr/~baris'
        a2.projects = [ 'pisi', 'tasma', 'plasma' ]
        a2.encode(xml)
        xml.writexml('/tmp/a2.xml')
        string = a2.format()

suite = unittest.makeSuite(XmlFileTestCase)

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

class AutoXmlTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database=False)

        class OtherInfo:
            __metaclass__ = xmlfile.autoxml
            t_BirthDate = [types.StringType, xmlfile.mandatory]
            t_Interest = [types.StringType, xmlfile.optional]
            t_CodesWith = [ [types.StringType], xmlfile.optional, 'CodesWith/Person']
        
        class A(xmlfile.XmlFile):
            __metaclass__ = xmlfile.autoxml
            t_Name = [types.StringType, xmlfile.mandatory]
            t_Description = [xmlfile.LocalText, xmlfile.mandatory]
            t_Number = [types.IntType, xmlfile.optional]
            t_Email = [types.StringType, xmlfile.optional]
            a_href = [types.StringType, xmlfile.mandatory]
            t_Projects = [ [types.StringType], xmlfile.mandatory, 'Project']
            t_OtherInfo = [ OtherInfo, xmlfile.optional ]
            s_Comment = [ xmlfile.Text, xmlfile.mandatory]
        
        self.A = A

    def testDeclaration(self):
        self.assertEqual(len(self.A.decoders), 8) # how many fields in A?
        self.assert_(hasattr(self.A, 'encode'))

    def testReadWrite(self):
        a = self.A()
        
        # test initializer
        self.assertEqual(a.href, None)
        
        # test read
        a.read('tests/a.xml')
        self.assert_(a.href.startswith('http'))
        self.assertEqual(a.number, 868)
        self.assertEqual(a.name, 'Eray Ozkural')
        self.assertEqual(len(a.projects), 3)
        self.assertEqual(len(a.otherInfo.codesWith), 4)

        self.assert_(not a.check())

        a.print_text(file('/tmp/a', 'w'))
        la = file('/tmp/a').readlines()
        self.assert_( util.any(lambda x:x.find('18071976')!=-1, la) )
        a.write('/tmp/a.xml')
        
    def testWriteRead(self):
        a = self.A()
        a.name = "Baris Metin"
        a.email = "baris@uludag.org.tr"
        a.description['tr'] = u'Melek, melek'
        a.comment = u'Bu da zibidi aslinda ama caktirmiyor'
        a.href = 'http://cekirdek.uludag.org.tr/~baris'
        a.otherInfo.birthDate = '30101979'
        a.projects = [ 'pisi', 'tasma', 'plasma' ]
        errs = a.check()
        if errs:
            self.fail( 'We got a bunch of errors: ' + str(errs)) 
        a.write('/tmp/a2.xml')

suite = unittest.makeSuite(AutoXmlTestCase)

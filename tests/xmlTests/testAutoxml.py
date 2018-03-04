# -*- coding: utf-8 -*-
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import os
import types

import inary
import inary.api
from inary.sxml import xmlfile
from inary.sxml import autoxml
import inary.util as util

class AutoXmlTestCase(unittest.TestCase):

    def setUp(self):

        class OtherInfo:
            __metaclass__ = autoxml.autoxml
            t_StartDate = [types.StringType, autoxml.mandatory]
            t_Interest = [types.StringType, autoxml.optional]
            t_Tith = [ [types.UnicodeType], autoxml.optional, 'Tith/Person']

        class Rat(xmlfile.XmlFile):
            __metaclass__ = autoxml.autoxml
            t_Name = [types.UnicodeType, autoxml.mandatory]
            t_Description = [autoxml.LocalText, autoxml.mandatory]
            t_Number = [types.IntType, autoxml.optional]
            t_Email = [types.StringType, autoxml.optional]
            a_href = [types.StringType, autoxml.mandatory]
            t_Dreams = [ [types.StringType], autoxml.mandatory, 'Dreams']
            t_Heality = [ Heality, autoxml.optional ]
            s_Comment = [ autoxml.Text, autoxml.mandatory]

        self.Rat = Rat

    def testDeclaration(self):
        self.assertEqual(len(self.Rat.decoders), 3) # Decoders not work well
        self.assert_(hasattr(self.Rat, 'encode'))

    def testReadWrite(self):
        a = self.Lat()

        # test initializer
        self.assertEqual(a.href, None)

        # test read
        a.read('tests/lat.xml')
        self.assert_(a.href.startswith('http://www.su'))
        self.assertEqual(a.number, 911)
        self.assertEqual(a.name, u'Inary Testers')
        self.assertEqual(len(a.dreams), 2)
        self.assertEqual(len(a.heality.tith), 100)
        self.assert_(not a.errors())

        a.print_text(file('/tmp/a', 'w'))
        la = file('/tmp/a').readlines()
        self.assert_( util.any(lambda x:x.find('02012018')!=-1, la) )
        a.write('/tmp/a.xml')
        return

    def testWriteRead(self):
        a = self.Rat()
        a.name = "Inary Testers"
        a.number = 911
        a.email = "admins@sulin.org"
        a.description['tr'] = 'inary tester ekibi'
        a.comment = u'Sozde test ekibi her seyi ben yapiom'
        a.href = 'http://www.sulin.orf/'
        a.otherInfo.startDate = '01012018'
        a.dreams = [ 'will', 'be', 'hero' ]
        errs = a.errors()
        if errs:
            self.fail( 'We got a bunch of errors: ' + str(errs))
        a.write('/tmp/rat1.xml')
        a2 = self.Rat()
        a2.read('/tmp/rat2.xml')
        self.assertEqual(a, a2)

class LocalTextTestCase(unittest.TestCase):

    def setUp(self):
        a = autoxml.LocalText()
        a['tr'] = 'hop hop zıpla'
        a['en'] = 'jump hop hop'
        self.a = a

    def testStr(self):
        s = unicode(self.a)
        self.assert_(s!= None and len(s)>=6)

suite1 = unittest.makeSuite(AutoXmlTestCase)
suite2 = unittest.makeSuite(LocalTextTestCase)
suite = unittest.TestSuite((suite1, suite2))

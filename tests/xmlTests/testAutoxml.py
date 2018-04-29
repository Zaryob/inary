# -*- coding: utf-8 -*-
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
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

import inary
import inary.api
from inary.sxml import xmlfile
from inary.sxml import autoxml
import inary.util as util

class AutoXmlTestCase(unittest.TestCase):

    def setUp(self):

        class OtherInfo(metaclass = autoxml.autoxml):
            t_StartDate = [str, autoxml.mandatory]
            t_Interest = [str, autoxml.optional]
            t_Tith = [ [bytes], autoxml.optional, 'Tith/Person']

        class Rat(xmlfile.XmlFile, metaclass = autoxml.autoxml):
            t_Name = [bytes, autoxml.mandatory]
            t_Description = [autoxml.LocalText, autoxml.mandatory]
            t_Number = [int, autoxml.optional]
            t_Email = [str, autoxml.optional]
            a_href = [str, autoxml.mandatory]
            t_Dreams = [ [str], autoxml.mandatory, 'Dreams']
            t_Heality = [ str, autoxml.optional ]
            s_Comment = [ autoxml.Text, autoxml.mandatory]
            a_otherInfo = [OtherInfo, autoxml.mandatory]

        self.Rat = Rat


    def testDeclaration(self):
        self.assertEqual(len(self.Rat.decoders), 8) # Decoders not work well
        self.assert_(hasattr(self.Rat, 'encode'))

    def testReadWrite(self):
        a = self.Rat()

        # test initializer
        self.assertEqual(a.href, None)

        # test read
        a.read('tests/rat.xml')
        self.assert_(a.href.startswith('http://www.su'))
        self.assertEqual(a.number, 911)
        self.assertEqual(a.name, 'Inary Testers')
        self.assertEqual(len(a.dreams), 3)
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
        a.comment = b'Sozde test ekibi her seyi ben yapiom'
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
        s = bytes(self.a)
        self.assert_(s!= None and len(s)>=6)

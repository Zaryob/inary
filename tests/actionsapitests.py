import unittest

from pisi.actionsapi import gnuconfig

class gnuConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.gnuconfig = gnuconfig.gnuconfig_findnewest()
    
    def testFindNewest(self):
        self.assert_ (self.gnuconfig >= '/usr/share/automake-1.4')

suite = unittest.makeSuite(gnuConfigTestCase)

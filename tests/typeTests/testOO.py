# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest
import os
import time

from inary import version
import inary.constants as constant
from inary.oo import *
from inary.util import Singleton

class OOTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testAutosuper(self):
        class A(metaclass = autosuper):
            def meth(self):
                return "A"
        class B(A):
            def meth(self):
                return "B" + self.__super.meth()
        class C(A):
            def meth(self):
                return "C" + self.__super.meth()
        class D(C, B):
            def meth(self):
                return "D" + self.__super.meth()

        self.assert_( D().meth() == "DCBA" )

    def testConstant(self):
        class A(metaclass = constant._constant):
            def __init__(self):
                self.a = 1
                self.b = 2
        mya = A()
        try:
            passed = False
            mya.a = 0
        except ConstError as e:
            passed = True
        self.assert_(passed)

    def testSingleton(self):
        class A(metaclass = Singleton):
            def __init__(self):
                self.a = time.time()
        a1 = A()
        a2 = A()
        self.assert_(a1 is a2)


suite = unittest.makeSuite(OOTestCase)

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Süleyman POYRAZ (Zaryob)
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

from inary.actionsapi import autotools
from inary.actionsapi import inarytools

WorkDir = "most-pre5.1-6"

def setup():
    autotools.configure()

def build():
    autotools.make()

def install():
    autotools.install()
    inarytools.dodoc("most.hlp", "COPYING*", "COPYRIGHT")

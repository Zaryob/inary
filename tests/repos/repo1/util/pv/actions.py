#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Süleyman POYRAZ (Zaryob)
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

from inary.actionsapi import autotools
from inary.actionsapi import inarytools
from inary.actionsapi import get

def setup():
    autotools.configure()

def build():
    autotools.make("CC=%s" % get.CC())

def check():
    autotools.make("test")

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    inarytools.dodoc("README", "doc/NEWS", "doc/TODO", "doc/COPYING")

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

from inary.actionsapi import autotools
from inary.actionsapi import get
from inary.actionsapi import inarytools
from inary.actionsapi import shelltools
from inary.actionsapi import pythonmodules

def setup():
 #   autotools.autoreconf("-vfi")
    autotools.configure("--disable-static")

def build():
    autotools.make("-j1")

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    inarytools.dodoc("AUTHORS", "COPYING", "ChangeLog")
    

    shelltools.export("LD_PRELOAD","%s/liblouis/.libs/liblouis.so.12" % get.curDIR())
    shelltools.cd("python")

    pythonmodules.install("--prefix=/usr --optimize=1")
    pythonmodules.install("--prefix=/usr --optimize=1",pyVer = "3")
 

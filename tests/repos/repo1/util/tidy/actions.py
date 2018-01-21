#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from inary.actionsapi import autotools
from inary.actionsapi import shelltools
from inary.actionsapi import inarytools
from inary.actionsapi import get

#WorkDir = "tidy-%s" % get.srcVERSION().split("_", 1)[1]

def setup():
    #shelltools.system("sh build/gnuauto/setup.sh")
    autotools.configure("--disable-static")
                         #--includedir=%s/usr/include/" % get.installDIR())

def build():
    autotools.make()

def install():
    autotools.install()

    #inarytools.dodoc("readme.txt")

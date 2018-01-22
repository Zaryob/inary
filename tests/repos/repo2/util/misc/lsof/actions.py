#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from inary.actionsapi import autotools
from inary.actionsapi import inarytools
from inary.actionsapi import shelltools
from inary.actionsapi import get

WorkDir = "lsof_%s_src" % get.srcVERSION()

def setup():
    shelltools.export("LINUX_BASE", "/proc")
    shelltools.export("LSOF_LDFLAGS", get.LDFLAGS())

    shelltools.touch(".neverInv")
    shelltools.system("./Configure -n linux")

def build():
    autotools.make('CC="%s" DEBUG="%s" all' % (get.CC(), get.CFLAGS()))

def install():
    inarytools.dosbin("lsof")

    inarytools.insinto("/usr/share/lsof/scripts", "scripts/*")

    inarytools.doman("lsof.8")
    inarytools.dodoc("00*")

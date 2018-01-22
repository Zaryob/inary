#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from inary.actionsapi import autotools
from inary.actionsapi import inarytools
from inary.actionsapi import shelltools

WorkDir = "."

def build():
    shelltools.cd("src")
    autotools.make()

def install():
    inarytools.dobin("src/uif2iso")

    inarytools.dodoc("uif2iso.txt", "README")

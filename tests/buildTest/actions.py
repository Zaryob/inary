#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from inary.actionsapi import shelltools
from inary.actionsapi import get
from inary.actionsapi import inarytools
from inary.actionsapi import mesontools


def install():
    shelltools.system("mkdir -p {}/usr/bin/".format(get.installDIR()))
    shelltools.system("install space {}/usr/bin/hello".format(get.installDIR()))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

import os
from inary.actionsapi import shelltools
from inary.actionsapi import get
from inary.actionsapi import inarytools
from inary.actionsapi import mesontools
from inary.actionsapi import cmaketools
from inary.actionsapi import autotools


def setup():
    pass


def build():
    pass


def install():
    os.chdir("../unibuild-master")
    autotools.install("DESTDIR={} ".format(get.installDIR()))

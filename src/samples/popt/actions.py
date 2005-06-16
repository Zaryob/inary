#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi.gnuconfig import *
from pisi.actionsapi.libtoolize import *
from pisi.actionsapi.autotools import *

def setup():
    gnuconfig_update()
#    libtoolize()
    configure( '--with-nls' )

def build():
    make()

def install():
    install()

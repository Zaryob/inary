#!/usr/bin/python
# -*- coding: utf-8 -*-

#import pisi.actionsapi.gnuconfig as gnuconfig
#import pisi.actionsapi.libtoolize as libtoolize
#import pisi.actionsapi.autotools as autotools

from pisi.actionsapi.gnuconfig import *
from pisi.actionsapi.autotools import *

def src_setup():
    gnuconfig_update()
#    libtoolize.libtoolize()
    configure( '--with-nls' )

def src_build():
    make()

def src_install():
    install()

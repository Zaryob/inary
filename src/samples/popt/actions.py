#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi.gnuconfig import *
from pisi.actionsapi.libtoolize import *
from pisi.actionsapi.autotools import *

def src_setup():
	gnuconfig_update()
#	libtoolize()
	configure( '--with-nls' )

def src_build():
	make()

def src_install():
	install()
